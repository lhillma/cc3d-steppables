{
  description = "Library of CC3D steppables in Python";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    cc3d.url = "git+ssh://git@gitlab.tue.nl/20235660/cc3d-flake";
  };

  outputs = { self, nixpkgs, ... }@inputs: {

    packages.x86_64-linux.cc3dslib = let
      pkgs = import nixpkgs { system = "x86_64-linux"; };
    in pkgs.python311Packages.buildPythonPackage {
      pname = "cc3dslib";
      version = "0.3.0";
      src = ./.;
      doCheck = false;
      meta = {
        description = "Library of CC3D steppables in Python";
      };

      build-system = with pkgs.python311Packages; [
        setuptools
      ];

      dependencies = with pkgs.python311Packages; [
        numpy
        h5py
      ];

      format = "pyproject";
    };

    packages.x86_64-linux.docker = let
      pkgs = import nixpkgs { system = "x86_64-linux"; };
      cc3d = inputs.cc3d.packages.x86_64-linux.cc3d;
      cc3d-player5 = inputs.cc3d.packages.x86_64-linux.cc3d-player5;
      cc3d-player5-wrapper = inputs.cc3d.packages.x86_64-linux.cc3d-player5-wrapper;
      cc3dslib = self.packages.x86_64-linux.cc3dslib;
    in pkgs.dockerTools.buildLayeredImage {
      name = "cc3dslib";
      tag = "latest";
      contents = with pkgs; [
        (python311.withPackages (ps: [
          cc3d
          cc3d-player5
          cc3dslib
        ]))
        cc3d-player5-wrapper
        bash
        coreutils
      ];

      config = {
        Cmd = [ "bash" ];
      };
    };

    packages.x86_64-linux.default = self.packages.x86_64-linux.cc3dslib;

    devShells.x86_64-linux = {
      cc3dslib = let
        pkgs = import nixpkgs { system = "x86_64-linux"; };
        cc3d = inputs.cc3d.packages.x86_64-linux.cc3d;
        cc3d-player5 = inputs.cc3d.packages.x86_64-linux.cc3d-player5;
        cc3d-player5-wrapper = inputs.cc3d.packages.x86_64-linux.cc3d-player5-wrapper;
        cc3dslib = self.packages.x86_64-linux.cc3dslib;
      in pkgs.mkShell {
        name = "cc3dslib";
        buildInputs = with pkgs; [
          (python311.withPackages (ps: [
            cc3d
            cc3d-player5
            cc3dslib
          ]))
          cc3d-player5-wrapper
        ];
      };

      default = self.devShells.x86_64-linux.cc3dslib;
    };

  };
}
