%global debug_package %{nil}

Name: python-ruamel-yaml
Epoch: 100
Version: 0.17.18
Release: 1%{?dist}
BuildArch: noarch
Summary: YAML 1.2 loader/dumper package for Python
License: MIT
URL: https://pypi.org/project/ruamel.yaml/#history
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: fdupes
BuildRequires: python-rpm-macros
BuildRequires: python3-devel
BuildRequires: python3-setuptools

%description
ruamel.yaml is a YAML 1.2 loader/dumper package for Python. It is a
derivative of Kirill Simonov’s PyYAML 3.11.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
%{__python3} setup.py build

%install
%{__python3} setup.py install --single-version-externally-managed --skip-build --root=%{buildroot} --prefix=%{_prefix}
find %{buildroot}%{python3_sitelib} -type f -name '*.pyc' -exec rm -rf {} \;
%fdupes -s %{buildroot}%{python3_sitelib}

%check

%if 0%{?suse_version} > 1500
%package -n python%{python3_version_nodots}-ruamel.yaml
Summary: YAML 1.2 loader/dumper package for Python
Requires: python3
Requires: python%{python3_version_nodots}-ruamel.yaml.clib
Provides: python3-ruamel.yaml = %{epoch}:%{version}-%{release}
Provides: python3dist(ruamel.yaml) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}-ruamel.yaml = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}dist(ruamel.yaml) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}-ruamel.yaml = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}dist(ruamel.yaml) = %{epoch}:%{version}-%{release}

%description -n python%{python3_version_nodots}-ruamel.yaml
ruamel.yaml is a YAML 1.2 loader/dumper package for Python. It is a
derivative of Kirill Simonov’s PyYAML 3.11.

%files -n python%{python3_version_nodots}-ruamel.yaml
%license LICENSE
%{python3_sitelib}/ruamel*
%{python3_sitelib}/ruamel.yaml*
%endif

%if 0%{?sle_version} > 150000
%package -n python3-ruamel.yaml
Summary: YAML 1.2 loader/dumper package for Python
Requires: python3
Requires: python3-ruamel.yaml.clib
Provides: python3-ruamel.yaml = %{epoch}:%{version}-%{release}
Provides: python3dist(ruamel.yaml) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}-ruamel.yaml = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}dist(ruamel.yaml) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}-ruamel.yaml = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}dist(ruamel.yaml) = %{epoch}:%{version}-%{release}

%description -n python3-ruamel.yaml
ruamel.yaml is a YAML 1.2 loader/dumper package for Python. It is a
derivative of Kirill Simonov’s PyYAML 3.11.

%files -n python3-ruamel.yaml
%license LICENSE
%{python3_sitelib}/ruamel*
%{python3_sitelib}/ruamel.yaml*
%endif

%if !(0%{?suse_version} > 1500) && !(0%{?sle_version} > 150000)
%package -n python3-ruamel-yaml
Summary: YAML 1.2 loader/dumper package for Python
Requires: python3
Requires: python3-ruamel-yaml-clib
Provides: python3-ruamel.yaml = %{epoch}:%{version}-%{release}
Provides: python3dist(ruamel.yaml) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}-ruamel.yaml = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}dist(ruamel.yaml) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}-ruamel.yaml = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}dist(ruamel.yaml) = %{epoch}:%{version}-%{release}

%description -n python3-ruamel-yaml
ruamel.yaml is a YAML 1.2 loader/dumper package for Python. It is a
derivative of Kirill Simonov’s PyYAML 3.11.

%files -n python3-ruamel-yaml
%license LICENSE
%{python3_sitelib}/ruamel*
%{python3_sitelib}/ruamel.yaml*
%endif

%changelog
