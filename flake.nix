{
  description = "dfint-installer built from release sources";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };

      version = "0.6.6";

      src = pkgs.fetchzip {
        url = "https://github.com/dfint/installer/archive/refs/tags/${version}.tar.gz";
        hash = "sha256-ZnFisZJCkR5LcorBTpROXsWpJWOTnwl4HE6JucR5nOI=";
        stripRoot = true;
      };

      runtimeLibs = with pkgs; [
        libxkbcommon
        libx11
        libxcursor
        libxrandr
        libxi
        libxcb
        wayland
        wayland-protocols
        libGL
        vulkan-loader
        alsa-lib
        udev
      ];

      dfint-installer = pkgs.rustPlatform.buildRustPackage {
        pname = "dfint-installer";
        inherit version;
        inherit src;

        cargoLock.lockFile = "${src}/Cargo.lock";

        nativeBuildInputs = with pkgs; [
          pkg-config
          makeWrapper
        ];

        buildInputs = runtimeLibs;

        postFixup = ''
          wrapProgram $out/bin/dfint-installer \
            --prefix LD_LIBRARY_PATH : "${pkgs.lib.makeLibraryPath runtimeLibs}"
        '';

        meta = {
          description = "Dwarf Fortress localization installer";
          homepage = "https://github.com/dfint/installer";
          platforms = [ "x86_64-linux" ];
          mainProgram = "dfint-installer";
        };
      };
    in
    {
      packages.${system} = {
        default = dfint-installer;
        dfint-installer = dfint-installer;
      };

      apps.${system}.default = {
        type = "app";
        program = "${dfint-installer}/bin/dfint-installer";
      };
    };
}
