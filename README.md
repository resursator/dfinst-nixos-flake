
# dfint-installer-nixos-flake

Nix flake for building and running [dfint-installer](https://github.com/dfint/installer) on NixOS and other Linux systems with Nix flakes enabled.

The flake packages **dfint-installer 0.6.6** directly from the upstream release sources. It provides a wrapped executable with the required runtime libraries, including X11, Wayland, OpenGL, Vulkan, ALSA and udev dependencies.

## Requirements

- Nix with flakes enabled
- `x86_64-linux`

## Usage

### Run without installing

Run the application directly from GitHub:

```bash
nix run github:resursator/dfinst-nixos-flake
```

### Build the package

```bash
nix build github:resursator/dfinst-nixos-flake
```

The resulting executable will be available at:

```text
./result/bin/dfint-installer
```

### Run from a local checkout

```bash
nix run .
```

### Install into your user profile

```bash
nix profile install github:resursator/dfinst-nixos-flake
```

After installation, run:

```bash
dfint-installer
```

## Package details

- **Upstream:** [dfint/installer](https://github.com/dfint/installer)
- **Version:** 0.6.6
- **Package attribute:** `.#dfint-installer`
- **Default package:** `.#default`
- **Default app:** `.#default`
- **Platform:** `x86_64-linux`

Runtime library paths are configured through a wrapper, so the application can find the libraries supplied by Nix.

## Development

Build the package:

```bash
nix build
```

Run it:

```bash
nix run
```

Inspect the flake outputs:

```bash
nix flake show
```

Update the `nixpkgs` input:

```bash
nix flake update
```

## License

See the [upstream repository](https://github.com/dfint/installer) for the original project's license. This repository provides Nix packaging for the upstream application.
