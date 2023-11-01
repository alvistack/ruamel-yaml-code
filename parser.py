# coding: utf-8

# The following YAML grammar is LL(1) and is parsed by a recursive descent
# parser.
#
# stream            ::= STREAM-START implicit_document? explicit_document*
#                                                                   STREAM-END
# implicit_document ::= block_node DOCUMENT-END*
# explicit_document ::= DIRECTIVE* DOCUMENT-START block_node? DOCUMENT-END*
# block_node_or_indentless_sequence ::=
#                       ALIAS
#                       | properties (block_content |
#                                                   indentless_block_sequence)?
#                       | block_content
#                       | indentless_block_sequence
# block_node        ::= ALIAS
#                       | properties block_content?
#                       | block_content
# flow_node         ::= ALIAS
#                       | properties flow_content?
#                       | flow_content
# properties        ::= TAG ANCHOR? | ANCHOR TAG?
# block_content     ::= block_collection | flow_collection | SCALAR
# flow_content      ::= flow_collection | SCALAR
# block_collection  ::= block_sequence | block_mapping
# flow_collection   ::= flow_sequence | flow_mapping
# block_sequence    ::= BLOCK-SEQUENCE-START (BLOCK-ENTRY block_node?)*
#                                                                   BLOCK-END
# indentless_sequence   ::= (BLOCK-ENTRY block_node?)+
# block_mapping     ::= BLOCK-MAPPING_START
#                       ((KEY block_node_or_indentless_sequence?)?
#                       (VALUE block_node_or_indentless_sequence?)?)*
#                       BLOCK-END
# flow_sequence     ::= FLOW-SEQUENCE-START
#                       (flow_sequence_entry FLOW-ENTRY)*
#                       flow_sequence_entry?
#                       FLOW-SEQUENCE-END
# flow_sequence_entry   ::= flow_node | KEY flow_node? (VALUE flow_node?)?
# flow_mapping      ::= FLOW-MAPPING-START
#                       (flow_mapping_entry FLOW-ENTRY)*
#                       flow_mapping_entry?
#                       FLOW-MAPPING-END
# flow_mapping_entry    ::= flow_node | KEY flow_node? (VALUE flow_node?)?
#
# FIRST sets:
#
# stream: { STREAM-START <}
# explicit_document: { DIRECTIVE DOCUMENT-START }
# implicit_document: FIRST(block_node)
# block_node: { ALIAS TAG ANCHOR SCALAR BLOCK-SEQUENCE-START
#                  BLOCK-MAPPING-START FLOW-SEQUENCE-START FLOW-MAPPING-START }
# flow_node: { ALIAS ANCHOR TAG SCALAR FLOW-SEQUENCE-START FLOW-MAPPING-START }
# block_content: { BLOCK-SEQUENCE-START BLOCK-MAPPING-START
#                               FLOW-SEQUENCE-START FLOW-MAPPING-START SCALAR }
# flow_content: { FLOW-SEQUENCE-START FLOW-MAPPING-START SCALAR }
# block_collection: { BLOCK-SEQUENCE-START BLOCK-MAPPING-START }
# flow_collection: { FLOW-SEQUENCE-START FLOW-MAPPING-START }
# block_sequence: { BLOCK-SEQUENCE-START }
# block_mapping: { BLOCK-MAPPING-START }
# block_node_or_indentless_sequence: { ALIAS ANCHOR TAG SCALAR
#               BLOCK-SEQUENCE-START BLOCK-MAPPING-START FLOW-SEQUENCE-START
#               FLOW-MAPPING-START BLOCK-ENTRY }
# indentless_sequence: { ENTRY }
# flow_collection: { FLOW-SEQUENCE-START FLOW-MAPPING-START }
# flow_sequence: { FLOW-SEQUENCE-START }
# flow_mapping: { FLOW-MAPPING-START }
# flow_sequence_entry: { ALIAS ANCHOR TAG SCALAR FLOW-SEQUENCE-START
#                                                    FLOW-MAPPING-START KEY }
# flow_mapping_entry: { ALIAS ANCHOR TAG SCALAR FLOW-SEQUENCE-START
#                                                    FLOW-MAPPING-START KEY }

# need to have full path with import, as pkg_resources tries to load parser.py in __init__.py
# only to not do anything with the package afterwards
# and for Jython too


from ruamel.yaml.error import MarkedYAMLError
from ruamel.yaml.tokens import *  # NOQA
from ruamel.yaml.events import *  # NOQA
from ruamel.yaml.scanner import Scanner, RoundTripScanner, ScannerError  # NOQA
from ruamel.yaml.scanner import BlankLineComment
from ruamel.yaml.comments import C_PRE, C_POST, C_SPLIT_ON_FIRST_BLANK
from ruamel.yaml.compat import nprint, nprintf  # NOQA
from ruamel.yaml.tag import Tag

from typing import Any, Dict, Optional, List, Optional  # NOQA

__all__ = ['Parser', 'RoundTripParser', 'ParserError']


def xprintf(*args: Any, **kw: Any) -> Any:
    return nprintf(*args, **kw)
    pass


class ParserError(MarkedYAMLError):
    pass


class Parser:
    # Since writing a recursive-descendant parser is a straightforward task, we
    # do not give many comments here.

    DEFAULT_TAGS = {'!': '!', '!!': 'tag:yaml.org,2002:'}

    def __init__(self, loader: Any) -> None:
        self.loader = loader
        if self.loader is not None and getattr(self.loader, '_parser', None) is None:
            self.loader._parser = self
        self.reset_parser()

    def reset_parser(self) -> None:
        # Reset the state attributes (to clear self-references)
        self.current_event = self.last_event = None
        self.tag_handles: Dict[Any, Any] = {}
        self.states: List[Any] = []
        self.marks: List[Any] = []
        self.state: Any = self.parse_stream_start

    def dispose(self) -> None:
        self.reset_parser()

    @property
    def scanner(self) -> Any:
        if hasattr(self.loader, 'typ'):
            return self.loader.scanner
        return self.loader._scanner

    @property
    def resolver(self) -> Any:
        if hasattr(self.loader, 'typ'):
            return self.loader.resolver
        return self.loader._resolver

    def check_event(self, *choices: Any) -> bool:
        # Check the type of the next event.
        if self.current_event is None:
            if self.state:
                self.current_event = self.state()
        if self.current_event is not None:
            if not choices:
                return True
            for choice in choices:
                if isinstance(self.current_event, choice):
                    return True
        return False

    def peek_event(self) -> Any:
        # Get the next event.
        if self.current_event is None:
            if self.state:
                self.current_event = self.state()
        return self.current_event

    def get_event(self) -> Any:
        # Get the next event and proceed further.
        if self.current_event is None:
            if self.state:
                self.current_event = self.state()
        # assert self.current_event is not None
        # if self.current_event.end_mark.line != self.peek_event().start_mark.line:
        xprintf('get_event', repr(self.current_event), self.peek_event().start_mark.line)
        self.last_event = value = self.current_event
        self.current_event = None
        return value

    # stream    ::= STREAM-START implicit_document? explicit_document*
    #                                                               STREAM-END
    # implicit_document ::= block_node DOCUMENT-END*
    # explicit_document ::= DIRECTIVE* DOCUMENT-START block_node? DOCUMENT-END*

    def parse_stream_start(self) -> Any:
        # Parse the stream start.
        token = self.scanner.get_token()
        self.move_token_comment(token)
        event = StreamStartEvent(token.start_mark, token.end_mark, encoding=token.encoding)

        # Prepare the next state.
        self.state = self.parse_implicit_document_start

        return event

    def parse_implicit_document_start(self) -> Any:
        # Parse an implicit document.
        if not self.scanner.check_token(DirectiveToken, DocumentStartToken, StreamEndToken):
            # don't need copy, as an implicit tag doesn't add tag_handles
            self.tag_handles = self.DEFAULT_TAGS
            token = self.scanner.peek_token()
            start_mark = end_mark = token.start_mark
            event = DocumentStartEvent(start_mark, end_mark, explicit=False)

            # Prepare the next state.
            self.states.append(self.parse_document_end)
            self.state = self.parse_block_node

            return event

        else:
            return self.parse_document_start()

    def parse_document_start(self) -> Any:
        # Parse any extra document end indicators.
        while self.scanner.check_token(DocumentEndToken):
            self.scanner.get_token()
        # Parse an explicit document.
        if not self.scanner.check_token(StreamEndToken):
            version, tags = self.process_directives()
            if not self.scanner.check_token(DocumentStartToken):
                raise ParserError(
                    None,
                    None,
                    "expected '<document start>', "
                    f'but found {self.scanner.peek_token().id,!r}',
                    self.scanner.peek_token().start_mark,
                )
            token = self.scanner.get_token()
            start_mark = token.start_mark
            end_mark = token.end_mark
            # if self.loader is not None and \
            #    end_mark.line != self.scanner.peek_token().start_mark.line:
            #     self.loader.scalar_after_indicator = False
            event: Any = DocumentStartEvent(
                start_mark,
                end_mark,
                explicit=True,
                version=version,
                tags=tags,
                comment=token.comment,
            )
            self.states.append(self.parse_document_end)
            self.state = self.parse_document_content
        else:
            # Parse the end of the stream.
            token = self.scanner.get_token()
            event = StreamEndEvent(token.start_mark, token.end_mark, comment=token.comment)
            assert not self.states
            assert not self.marks
            self.state = None
        return event

    def parse_document_end(self) -> Any:
        # Parse the document end.
        token = self.scanner.peek_token()
        start_mark = end_mark = token.start_mark
        explicit = False
        if self.scanner.check_token(DocumentEndToken):
            token = self.scanner.get_token()
            # if token.end_mark.line != self.peek_event().start_mark.line:
            pt = self.scanner.peek_token()
            if not isinstance(pt, StreamEndToken) and (
                token.end_mark.line == pt.start_mark.line
            ):
                raise ParserError(
                    None,
                    None,
                    'found non-comment content after document end marker, '
                    f'{self.scanner.peek_token().id,!r}',
                    self.scanner.peek_token().start_mark,
                )
            end_mark = token.end_mark
            explicit = True
        event = DocumentEndEvent(start_mark, end_mark, explicit=explicit)

        # Prepare the next state.
        if self.resolver.processing_version == (1, 1):
            self.state = self.parse_document_start
        else:
            if explicit:
                # found a document end marker, can be followed by implicit document
                self.state = self.parse_implicit_document_start
            else:
                self.state = self.parse_document_start

        return event

    def parse_document_content(self) -> Any:
        if self.scanner.check_token(
            DirectiveToken, DocumentStartToken, DocumentEndToken, StreamEndToken,
        ):
            event = self.process_empty_scalar(self.scanner.peek_token().start_mark)
            self.state = self.states.pop()
            return event
        else:
            return self.parse_block_node()

    def process_directives(self) -> Any:
        yaml_version = None
        self.tag_handles = {}
        while self.scanner.check_token(DirectiveToken):
            token = self.scanner.get_token()
            if token.name == 'YAML':
                if yaml_version is not None:
                    raise ParserError(
                        None, None, 'found duplicate YAML directive', token.start_mark,
                    )
                major, minor = token.value
                if major != 1:
                    raise ParserError(
                        None,
                        None,
                        'found incompatible YAML document (version 1.* is required)',
                        token.start_mark,
                    )
                yaml_version = token.value
            elif token.name == 'TAG':
                handle, prefix = token.value
                if handle in self.tag_handles:
                    raise ParserError(
                        None, None, f'duplicate tag handle {handle!r}', token.start_mark,
                    )
                self.tag_handles[handle] = prefix
        if bool(self.tag_handles):
            value: Any = (yaml_version, self.tag_handles.copy())
        else:
            value = yaml_version, None
        if self.loader is not None and hasattr(self.loader, 'tags'):
            self.loader.version = yaml_version
            if self.loader.tags is None:
                self.loader.tags = {}
            for k in self.tag_handles:
                self.loader.tags[k] = self.tag_handles[k]
                self.loader.doc_infos[-1].tags.append((k, self.tag_handles[k]))
        for key in self.DEFAULT_TAGS:
            if key not in self.tag_handles:
                self.tag_handles[key] = self.DEFAULT_TAGS[key]
        return value

    # block_node_or_indentless_sequence ::= ALIAS
    #               | properties (block_content | indentless_block_sequence)?
    #               | block_content
    #               | indentless_block_sequence
    # block_node    ::= ALIAS
    #                   | properties block_content?
    #                   | block_content
    # flow_node     ::= ALIAS
    #                   | properties flow_content?
    #                   | flow_content
    # properties    ::= TAG ANCHOR? | ANCHOR TAG?
    # block_content     ::= block_collection | flow_collection | SCALAR
    # flow_content      ::= flow_collection | SCALAR
    # block_collection  ::= block_sequence | block_mapping
    # flow_collection   ::= flow_sequence | flow_mapping

    def parse_block_node(self) -> Any:
        return self.parse_node(block=True)

    def parse_flow_node(self) -> Any:
        return self.parse_node()

    def parse_block_node_or_indentless_sequence(self) -> Any:
        return self.parse_node(block=True, indentless_sequence=True)

    # def transform_tag(self, handle: Any, suffix: Any) -> Any:
    #     return self.tag_handles[handle] + suffix

    def select_tag_transform(self, tag: Tag) -> None:
        if tag is None:
            return
        tag.select_transform(False)

    def parse_node(self, block: bool = False, indentless_sequence: bool = False) -> Any:
        if self.scanner.check_token(AliasToken):
            token = self.scanner.get_token()
            event: Any = AliasEvent(token.value, token.start_mark, token.end_mark)
            self.state = self.states.pop()
            return event

        anchor = None
        tag = None
        start_mark = end_mark = tag_mark = None
        if self.scanner.check_token(AnchorToken):
            token = self.scanner.get_token()
            self.move_token_comment(token)
            start_mark = token.start_mark
            end_mark = token.end_mark
            anchor = token.value
            if self.scanner.check_token(TagToken):
                token = self.scanner.get_token()
                tag_mark = token.start_mark
                end_mark = token.end_mark
                # tag = token.value
                tag = Tag(
                    handle=token.value[0], suffix=token.value[1], handles=self.tag_handles,
                )
        elif self.scanner.check_token(TagToken):
            token = self.scanner.get_token()
            try:
                self.move_token_comment(token)
            except NotImplementedError:
                pass
            start_mark = tag_mark = token.start_mark
            end_mark = token.end_mark
            # tag = token.value
            tag = Tag(handle=token.value[0], suffix=token.value[1], handles=self.tag_handles)
            if self.scanner.check_token(AnchorToken):
                token = self.scanner.get_token()
                start_mark = tag_mark = token.start_mark
                end_mark = token.end_mark
                anchor = token.value
        if tag is not None:
            self.select_tag_transform(tag)
            if tag.check_handle():
                raise ParserError(
                    'while parsing a node',
                    start_mark,
                    f'found undefined tag handle {tag.handle!r}',
                    tag_mark,
                )
        if start_mark is None:
            start_mark = end_mark = self.scanner.peek_token().start_mark
        event = None
        implicit = tag is None or str(tag) == '!'
        if indentless_sequence and self.scanner.check_token(BlockEntryToken):
            comment = None
            pt = self.scanner.peek_token()
            if self.loader and self.loader.comment_handling is None:
                if pt.comment and pt.comment[0]:
                    comment = [pt.comment[0], []]
                    pt.comment[0] = None
                elif pt.comment and pt.comment[0] is None and pt.comment[1]:
                    comment = [None, pt.comment[1]]
                    pt.comment[1] = None
            elif self.loader:
                if pt.comment:
                    comment = pt.comment
            end_mark = self.scanner.peek_token().end_mark
            event = SequenceStartEvent(
                anchor, tag, implicit, start_mark, end_mark, flow_style=False, comment=comment,
            )
            self.state = self.parse_indentless_sequence_entry
            return event

        if self.scanner.check_token(ScalarToken):
            token = self.scanner.get_token()
            # self.scanner.peek_token_same_line_comment(token)
            end_mark = token.end_mark
            if (token.plain and tag is None) or str(tag) == '!':
                dimplicit = (True, False)
            elif tag is None:
                dimplicit = (False, True)
            else:
                dimplicit = (False, False)
            event = ScalarEvent(
                anchor,
                tag,
                dimplicit,
                token.value,
                start_mark,
                end_mark,
                style=token.style,
                comment=token.comment,
            )
            self.state = self.states.pop()
        elif self.scanner.check_token(FlowSequenceStartToken):
            pt = self.scanner.peek_token()
            end_mark = pt.end_mark
            event = SequenceStartEvent(
                anchor,
                tag,
                implicit,
                start_mark,
                end_mark,
                flow_style=True,
                comment=pt.comment,
            )
            self.state = self.parse_flow_sequence_first_entry
        elif self.scanner.check_token(FlowMappingStartToken):
            pt = self.scanner.peek_token()
            end_mark = pt.end_mark
            event = MappingStartEvent(
                anchor,
                tag,
                implicit,
                start_mark,
                end_mark,
                flow_style=True,
                comment=pt.comment,
            )
            self.state = self.parse_flow_mapping_first_key
        elif block and self.scanner.check_token(BlockSequenceStartToken):
            end_mark = self.scanner.peek_token().start_mark
            # should inserting the comment be dependent on the
            # indentation?
            pt = self.scanner.peek_token()
            comment = pt.comment
            # nprint('pt0', type(pt))
            if comment is None or comment[1] is None:
                comment = pt.split_old_comment()
            # nprint('pt1', comment)
            event = SequenceStartEvent(
                anchor, tag, implicit, start_mark, end_mark, flow_style=False, comment=comment,
            )
            self.state = self.parse_block_sequence_first_entry
        elif block and self.scanner.check_token(BlockMappingStartToken):
            end_mark = self.scanner.peek_token().start_mark
            comment = self.scanner.peek_token().comment
            event = MappingStartEvent(
                anchor, tag, implicit, start_mark, end_mark, flow_style=False, comment=comment,
            )
            self.state = self.parse_block_mapping_first_key
        elif anchor is not None or tag is not None:
            # Empty scalars are allowed even if a tag or an anchor is
            # specified.
            event = ScalarEvent(anchor, tag, (implicit, False), "", start_mark, end_mark)
            self.state = self.states.pop()
        else:
            if block:
                node = 'block'
            else:
                node = 'flow'
            token = self.scanner.peek_token()
            raise ParserError(
                f'while parsing a {node!s} node',
                start_mark,
                f'expected the node content, but found {token.id!r}',
                token.start_mark,
            )
        return event

    # block_sequence ::= BLOCK-SEQUENCE-START (BLOCK-ENTRY block_node?)*
    #                                                               BLOCK-END

    def parse_block_sequence_first_entry(self) -> Any:
        token = self.scanner.get_token()
        # move any comment from start token
        # self.move_token_comment(token)
        self.marks.append(token.start_mark)
        return self.parse_block_sequence_entry()

    def parse_block_sequence_entry(self) -> Any:
        if self.scanner.check_token(BlockEntryToken):
            token = self.scanner.get_token()
            self.move_token_comment(token)
            if not self.scanner.check_token(BlockEntryToken, BlockEndToken):
                self.states.append(self.parse_block_sequence_entry)
                return self.parse_block_node()
            else:
                self.state = self.parse_block_sequence_entry
                return self.process_empty_scalar(token.end_mark)
        if not self.scanner.check_token(BlockEndToken):
            token = self.scanner.peek_token()
            raise ParserError(
                'while parsing a block collection',
                self.marks[-1],
                f'expected <block end>, but found {token.id!r}',
                token.start_mark,
            )
        token = self.scanner.get_token()  # BlockEndToken
        event = SequenceEndEvent(token.start_mark, token.end_mark, comment=token.comment)
        self.state = self.states.pop()
        self.marks.pop()
        return event

    # indentless_sequence ::= (BLOCK-ENTRY block_node?)+

    # indentless_sequence?
    # sequence:
    # - entry
    #  - nested

    def parse_indentless_sequence_entry(self) -> Any:
        if self.scanner.check_token(BlockEntryToken):
            token = self.scanner.get_token()
            self.move_token_comment(token)
            if not self.scanner.check_token(
                BlockEntryToken, KeyToken, ValueToken, BlockEndToken,
            ):
                self.states.append(self.parse_indentless_sequence_entry)
                return self.parse_block_node()
            else:
                self.state = self.parse_indentless_sequence_entry
                return self.process_empty_scalar(token.end_mark)
        token = self.scanner.peek_token()
        c = None
        if self.loader and self.loader.comment_handling is None:
            c = token.comment
            start_mark = token.start_mark
        else:
            start_mark = self.last_event.end_mark  # type: ignore
            c = self.distribute_comment(token.comment, start_mark.line)  # type: ignore
        event = SequenceEndEvent(start_mark, start_mark, comment=c)
        self.state = self.states.pop()
        return event

    # block_mapping     ::= BLOCK-MAPPING_START
    #                       ((KEY block_node_or_indentless_sequence?)?
    #                       (VALUE block_node_or_indentless_sequence?)?)*
    #                       BLOCK-END

    def parse_block_mapping_first_key(self) -> Any:
        token = self.scanner.get_token()
        self.marks.append(token.start_mark)
        return self.parse_block_mapping_key()

    def parse_block_mapping_key(self) -> Any:
        if self.scanner.check_token(KeyToken):
            token = self.scanner.get_token()
            self.move_token_comment(token)
            if not self.scanner.check_token(KeyToken, ValueToken, BlockEndToken):
                self.states.append(self.parse_block_mapping_value)
                return self.parse_block_node_or_indentless_sequence()
            else:
                self.state = self.parse_block_mapping_value
                return self.process_empty_scalar(token.end_mark)
        if self.resolver.processing_version > (1, 1) and self.scanner.check_token(ValueToken):
            self.state = self.parse_block_mapping_value
            return self.process_empty_scalar(self.scanner.peek_token().start_mark)
        if not self.scanner.check_token(BlockEndToken):
            token = self.scanner.peek_token()
            raise ParserError(
                'while parsing a block mapping',
                self.marks[-1],
                f'expected <block end>, but found {token.id!r}',
                token.start_mark,
            )
        token = self.scanner.get_token()
        self.move_token_comment(token)
        event = MappingEndEvent(token.start_mark, token.end_mark, comment=token.comment)
        self.state = self.states.pop()
        self.marks.pop()
        return event

    def parse_block_mapping_value(self) -> Any:
        if self.scanner.check_token(ValueToken):
            token = self.scanner.get_token()
            # value token might have post comment move it to e.g. block
            if self.scanner.check_token(ValueToken):
                self.move_token_comment(token)
            else:
                if not self.scanner.check_token(KeyToken):
                    self.move_token_comment(token, empty=True)
                # else: empty value for this key cannot move token.comment
            if not self.scanner.check_token(KeyToken, ValueToken, BlockEndToken):
                self.states.append(self.parse_block_mapping_key)
                return self.parse_block_node_or_indentless_sequence()
            else:
                self.state = self.parse_block_mapping_key
                comment = token.comment
                if comment is None:
                    token = self.scanner.peek_token()
                    comment = token.comment
                    if comment:
                        token._comment = [None, comment[1]]
                        comment = [comment[0], None]
                return self.process_empty_scalar(token.end_mark, comment=comment)
        else:
            self.state = self.parse_block_mapping_key
            token = self.scanner.peek_token()
            return self.process_empty_scalar(token.start_mark)

    # flow_sequence     ::= FLOW-SEQUENCE-START
    #                       (flow_sequence_entry FLOW-ENTRY)*
    #                       flow_sequence_entry?
    #                       FLOW-SEQUENCE-END
    # flow_sequence_entry   ::= flow_node | KEY flow_node? (VALUE flow_node?)?
    #
    # Note that while production rules for both flow_sequence_entry and
    # flow_mapping_entry are equal, their interpretations are different.
    # For `flow_sequence_entry`, the part `KEY flow_node? (VALUE flow_node?)?`
    # generate an inline mapping (set syntax).

    def parse_flow_sequence_first_entry(self) -> Any:
        token = self.scanner.get_token()
        self.marks.append(token.start_mark)
        return self.parse_flow_sequence_entry(first=True)

    def parse_flow_sequence_entry(self, first: bool = False) -> Any:
        if not self.scanner.check_token(FlowSequenceEndToken):
            if not first:
                if self.scanner.check_token(FlowEntryToken):
                    self.scanner.get_token()
                else:
                    token = self.scanner.peek_token()
                    raise ParserError(
                        'while parsing a flow sequence',
                        self.marks[-1],
                        f"expected ',' or ']', but got {token.id!r}",
                        token.start_mark,
                    )

            if self.scanner.check_token(KeyToken):
                token = self.scanner.peek_token()
                event: Any = MappingStartEvent(
                    None, None, True, token.start_mark, token.end_mark, flow_style=True,
                )
                self.state = self.parse_flow_sequence_entry_mapping_key
                return event
            elif not self.scanner.check_token(FlowSequenceEndToken):
                self.states.append(self.parse_flow_sequence_entry)
                return self.parse_flow_node()
        token = self.scanner.get_token()
        event = SequenceEndEvent(token.start_mark, token.end_mark, comment=token.comment)
        self.state = self.states.pop()
        self.marks.pop()
        return event

    def parse_flow_sequence_entry_mapping_key(self) -> Any:
        token = self.scanner.get_token()
        if not self.scanner.check_token(ValueToken, FlowEntryToken, FlowSequenceEndToken):
            self.states.append(self.parse_flow_sequence_entry_mapping_value)
            return self.parse_flow_node()
        else:
            self.state = self.parse_flow_sequence_entry_mapping_value
            return self.process_empty_scalar(token.end_mark)

    def parse_flow_sequence_entry_mapping_value(self) -> Any:
        if self.scanner.check_token(ValueToken):
            token = self.scanner.get_token()
            if not self.scanner.check_token(FlowEntryToken, FlowSequenceEndToken):
                self.states.append(self.parse_flow_sequence_entry_mapping_end)
                return self.parse_flow_node()
            else:
                self.state = self.parse_flow_sequence_entry_mapping_end
                return self.process_empty_scalar(token.end_mark)
        else:
            self.state = self.parse_flow_sequence_entry_mapping_end
            token = self.scanner.peek_token()
            return self.process_empty_scalar(token.start_mark)

    def parse_flow_sequence_entry_mapping_end(self) -> Any:
        self.state = self.parse_flow_sequence_entry
        token = self.scanner.peek_token()
        return MappingEndEvent(token.start_mark, token.start_mark)

    # flow_mapping  ::= FLOW-MAPPING-START
    #                   (flow_mapping_entry FLOW-ENTRY)*
    #                   flow_mapping_entry?
    #                   FLOW-MAPPING-END
    # flow_mapping_entry    ::= flow_node | KEY flow_node? (VALUE flow_node?)?

    def parse_flow_mapping_first_key(self) -> Any:
        token = self.scanner.get_token()
        self.marks.append(token.start_mark)
        return self.parse_flow_mapping_key(first=True)

    def parse_flow_mapping_key(self, first: Any = False) -> Any:
        if not self.scanner.check_token(FlowMappingEndToken):
            if not first:
                if self.scanner.check_token(FlowEntryToken):
                    self.scanner.get_token()
                else:
                    token = self.scanner.peek_token()
                    raise ParserError(
                        'while parsing a flow mapping',
                        self.marks[-1],
                        f"expected ',' or '}}', but got {token.id!r}",
                        token.start_mark,
                    )
            if self.scanner.check_token(KeyToken):
                token = self.scanner.get_token()
                if not self.scanner.check_token(
                    ValueToken, FlowEntryToken, FlowMappingEndToken,
                ):
                    self.states.append(self.parse_flow_mapping_value)
                    return self.parse_flow_node()
                else:
                    self.state = self.parse_flow_mapping_value
                    return self.process_empty_scalar(token.end_mark)
            elif self.resolver.processing_version > (1, 1) and self.scanner.check_token(
                ValueToken,
            ):
                self.state = self.parse_flow_mapping_value
                return self.process_empty_scalar(self.scanner.peek_token().end_mark)
            elif not self.scanner.check_token(FlowMappingEndToken):
                self.states.append(self.parse_flow_mapping_empty_value)
                return self.parse_flow_node()
        token = self.scanner.get_token()
        event = MappingEndEvent(token.start_mark, token.end_mark, comment=token.comment)
        self.state = self.states.pop()
        self.marks.pop()
        return event

    def parse_flow_mapping_value(self) -> Any:
        if self.scanner.check_token(ValueToken):
            token = self.scanner.get_token()
            if not self.scanner.check_token(FlowEntryToken, FlowMappingEndToken):
                self.states.append(self.parse_flow_mapping_key)
                return self.parse_flow_node()
            else:
                self.state = self.parse_flow_mapping_key
                return self.process_empty_scalar(token.end_mark)
        else:
            self.state = self.parse_flow_mapping_key
            token = self.scanner.peek_token()
            return self.process_empty_scalar(token.start_mark)

    def parse_flow_mapping_empty_value(self) -> Any:
        self.state = self.parse_flow_mapping_key
        return self.process_empty_scalar(self.scanner.peek_token().start_mark)

    def process_empty_scalar(self, mark: Any, comment: Any = None) -> Any:
        return ScalarEvent(None, None, (True, False), "", mark, mark, comment=comment)

    def move_token_comment(
        self, token: Any, nt: Optional[Any] = None, empty: Optional[bool] = False,
    ) -> Any:
        pass


class RoundTripParser(Parser):
    """roundtrip is a safe loader, that wants to see the unmangled tag"""

    def select_tag_transform(self, tag: Tag) -> None:
        if tag is None:
            return
        tag.select_transform(True)

    def move_token_comment(
        self, token: Any, nt: Optional[Any] = None, empty: Optional[bool] = False,
    ) -> Any:
        token.move_old_comment(self.scanner.peek_token() if nt is None else nt, empty=empty)


class RoundTripParserSC(RoundTripParser):
    """roundtrip is a safe loader, that wants to see the unmangled tag"""

    # some of the differences are based on the superclass testing
    # if self.loader.comment_handling is not None

    def move_token_comment(
        self: Any, token: Any, nt: Any = None, empty: Optional[bool] = False,
    ) -> None:
        token.move_new_comment(self.scanner.peek_token() if nt is None else nt, empty=empty)

    def distribute_comment(self, comment: Any, line: Any) -> Any:
        # ToDo, look at indentation of the comment to determine attachment
        if comment is None:
            return None
        if not comment[0]:
            return None
        # if comment[0][0] != line + 1:
        #     nprintf('>>>dcxxx', comment, line)
        assert comment[0][0] == line + 1
        # if comment[0] - line > 1:
        #     return
        typ = self.loader.comment_handling & 0b11
        # nprintf('>>>dca', comment, line, typ)
        if typ == C_POST:
            return None
        if typ == C_PRE:
            c = [None, None, comment[0]]
            comment[0] = None
            return c
        # nprintf('>>>dcb', comment[0])
        for _idx, cmntidx in enumerate(comment[0]):
            # nprintf('>>>dcb', cmntidx)
            if isinstance(self.scanner.comments[cmntidx], BlankLineComment):
                break
        else:
            return None  # no space found
        if _idx == 0:
            return None  # first line was blank
        # nprintf('>>>dcc', idx)
        if typ == C_SPLIT_ON_FIRST_BLANK:
            c = [None, None, comment[0][:_idx]]
            comment[0] = comment[0][_idx:]
            return c
        raise NotImplementedError  # reserved
