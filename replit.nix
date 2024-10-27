{pkgs}: {
  deps = [
    pkgs.rustc
    pkgs.pkg-config
    pkgs.libxcrypt
    pkgs.libiconv
    pkgs.cargo
    pkgs.poppler_utils
    pkgs.openssl
    pkgs.postgresql
  ];
}
