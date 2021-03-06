# centos/sclo spec file for php-pecl-ssh2, from:
#
# remirepo spec file for php-pecl-ssh2
# with SCL compatibility
#
# Copyright (c) 2011-2019 Remi Collet
#
# Fedora spec file for php-pecl-ssh2
#
# License: MIT
#
# Please, preserve the changelog entries
#
%if 0%{?scl:1}
%global sub_prefix %{scl_prefix}
%if "%{scl}" == "rh-php70"
%global sub_prefix sclo-php70-
%endif
%if "%{scl}" == "rh-php71"
%global sub_prefix sclo-php71-
%endif
%if "%{scl}" == "rh-php72"
%global sub_prefix sclo-php72-
%endif
%if "%{scl}" == "rh-php73"
%global sub_prefix sclo-php73-
%endif
%scl_package       php-pecl-ssh2
%endif

%global pecl_name  ssh2
%global ini_name   40-%{pecl_name}.ini

Name:           %{?sub_prefix}php-pecl-ssh2
Version:        1.2
Release:        1%{?dist}
Summary:        Bindings for the libssh2 library

%global buildver %(pkg-config --silence-errors --modversion libssh2  2>/dev/null || echo 65536)

License:        PHP
Group:          Development/Languages
URL:            http://pecl.php.net/package/%{pecl_name}
Source0:        http://pecl.php.net/get/%{pecl_name}-%{version}.tgz

BuildRequires:  libssh2-devel >= 1.2
BuildRequires:  %{?scl_prefix}php-devel > 7
BuildRequires:  %{?scl_prefix}php-pear

Requires:       %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires:       %{?scl_prefix}php(api) = %{php_core_api}
Requires:       libssh2%{?_isa}  >= %{buildver}

Provides:       %{?scl_prefix}php-%{pecl_name} = %{version}
Provides:       %{?scl_prefix}php-%{pecl_name}%{?_isa} = %{version}
Provides:       %{?scl_prefix}php-pecl(%{pecl_name}) = %{version}
Provides:       %{?scl_prefix}php-pecl(%{pecl_name})%{?_isa} = %{version}
%if "%{?scl_prefix}" != "%{?sub_prefix}"
Provides:       %{?scl_prefix}php-pecl-%{pecl_name}          = %{version}-%{release}
Provides:       %{?scl_prefix}php-pecl-%{pecl_name}%{?_isa}  = %{version}-%{release}
%endif

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter private shared
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
Bindings to the libssh2 library which provide access to resources
(shell, remote exec, tunneling, file transfer) on a remote machine using
a secure cryptographic transport.

Documentation: http://php.net/ssh2


%prep
%setup -c -q
mv %{pecl_name}-%{version} NTS

# Don't install/register tests
sed -e 's/role="test"/role="src"/' \
    %{?_licensedir:-e '/LICENSE/s/role="doc"/role="src"/' } \
    -i package.xml

cd NTS
extver=$(sed -n '/#define PHP_SSH2_VERSION/{s/.*\t"//;s/".*$//;p}' php_ssh2.h)
if test "x${extver}" != "x%{version}%{?gh_date:-dev}"; then
   : Error: Upstream version is now ${extver}, expecting %{version}%{?gh_date:-dev}.
   : Update the pdover macro and rebuild.
   exit 1
fi
cd ..

cat > %{ini_name} << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
EOF


%build
cd NTS
%{_bindir}/phpize
%configure  --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}


%install
make -C NTS install INSTALL_ROOT=%{buildroot}

# Install XML package description
install -Dpm 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# install config file
install -Dpm644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Documentation
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done



%check
: Minimal load test for NTS extension
%{__php} --no-php-ini \
    --define extension_dir=%{buildroot}%{php_extdir} \
    --define extension=%{pecl_name}.so \
    --modules | grep %{pecl_name}


# when pear installed alone, after us
%triggerin -- %{?scl_prefix}php-pear
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

# posttrans as pear can be installed after us
%posttrans
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

%postun
if [ $1 -eq 0 -a -x %{__pecl} ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%{?_licensedir:%license NTS/LICENSE}
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so


%changelog
* Mon Oct 28 2019 Remi Collet <remi@remirepo.net> - 1.2-1
- Update to 1.2

* Thu Nov 15 2018 Remi Collet <remi@remirepo.net> - 1.1.2-2
- build for sclo-php72
- add upstream patches for PHP 7+

* Fri Jan 19 2018 Remi Collet <remi@remirepo.net> - 1.1.2-1
- cleanup for centos/sclo

* Tue Aug  1 2017 Remi Collet <remi@remirepo.net> - 1.1.2-1
- Update to 1.1.2 (alpha, no change)

* Tue Jul 18 2017 Remi Collet <remi@remirepo.net> - 1.1.1-2
- rebuild for PHP 7.2.0beta1 new API

* Mon Jun 26 2017 Remi Collet <remi@remirepo.net> - 1.1.1-1
- Update to 1.1.1 (alpha, no change)

* Wed Jun 21 2017 Remi Collet <remi@remirepo.net> - 1.1-6
- rebuild for 7.2.0alpha2

* Wed Jun 14 2017 Remi Collet <remi@remirepo.net> - 1.1-5
- Update to 1.1 (alpha)

* Thu Dec  1 2016 Remi Collet <remi@fedoraproject.org> - 1.0-5
- rebuild with PHP 7.1.0 GA

* Thu Nov 10 2016 Remi Collet <remi@fedoraproject.org> - 1.0-4
- add patch for parse_url change in PHP 7.0.13

* Wed Sep 14 2016 Remi Collet <remi@fedoraproject.org> - 1.0-2
- rebuild for PHP 7.1 new API version

* Sun Jun 12 2016 Remi Collet <remi@fedoraproject.org> - 1.0-1
- update to 1.0

* Wed Jan 13 2016 Remi Collet <remi@fedoraproject.org> - 0.13-0.1.20160113git50d97a5
- update to 0.13-dev, git snapshot, for PHP 7

* Tue Jun 23 2015 Remi Collet <remi@fedoraproject.org> - 0.12-6
- allow build against rh-php56 (as more-php56)
- drop runtime dependency on pear, new scriptlets

* Wed Dec 24 2014 Remi Collet <remi@fedoraproject.org> - 0.12-5.1
- Fedora 21 SCL mass rebuild

* Sat Dec 20 2014 Remi Collet <remi@fedoraproject.org> - 0.12-5
- rebuild for new libssh2 in EL-5
- ensure dependency on libssh2 used at buildtime

* Mon Aug 25 2014 Remi Collet <rcollet@redhat.com> - 0.12-4
- improve SCL build

* Thu Apr 17 2014 Remi Collet <remi@fedoraproject.org> - 0.12-3
- add numerical prefix to extension configuration file (php 5.6)

* Sat Nov 30 2013 Remi Collet <RPMS@FamilleCollet.com> - 0.12-2
- cleanups for Copr
- adap for SCL
- install doc in pecl doc_dir

* Fri Nov 30 2012 Remi Collet <RPMS@FamilleCollet.com> - 0.12-1.1
- also provides php-ssh2

* Thu Oct 18 2012 Remi Collet <RPMS@FamilleCollet.com> - 0.12-1
- update to 0.12
- raise dependency on libssh2 >= 1.2

* Sun Nov 13 2011 Remi Collet <remi@fedoraproject.org> - 0.11.3-2
- build against php 5.4

* Tue Oct 04 2011 Remi Collet <RPMS@FamilleCollet.com> - 0.11.3-1
- update to 0.11.3
- zts extension

* Tue Aug 16 2011 Remi Collet <RPMS@FamilleCollet.com> - 0.11.2-1.1
- EL-5 rebuild for libssh2
- add filter

* Sat Apr 16 2011 Remi Collet <RPMS@FamilleCollet.com> - 0.11.2-1
- update to 0.11.2
- add minimal %%check

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Jan 14 2010 Chris Weyl <cweyl@alumni.drew.edu> 0.11.0-6
- bump for libssh2 rebuild


* Mon Sep 21 2009 Chris Weyl <cweyl@alumni.drew.edu> - 0.11.0-5
- rebuild for libssh2 1.2

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun Jul 12 2009 Remi Collet <Fedora@FamilleCollet.com> - 0.11.0-3
- add ssh2-php53.patch
- rebuild for new PHP 5.3.0 ABI (20090626)

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Dec 20 2008 Itamar Reis Peixoto <itamar@ispbrasil.com.br> 0.11.0-1
- convert package.xml to V2 format, update to 0.11.0 #BZ 476405

* Sat Nov 15 2008 Itamar Reis Peixoto <itamar@ispbrasil.com.br> 0.10-2
- Install pecl xml, license and readme files

* Wed Jul 16 2008 Itamar Reis Peixoto <itamar@ispbrasil.com.br> 0.10-1
- Initial release
