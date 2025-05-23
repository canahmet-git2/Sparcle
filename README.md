# Sparcle v1.1

> A desktop node-based VFX builder for creating ultra-small, perfectly looping particle effects for Spine animations in slot games.

## Features

- 🎨 **Node-Based Editor**: Intuitive visual programming interface using Rete.js
- 🔄 **Perfect Loops**: Seamless animation loops with customizable duration (0.25 – 10s)
- 📦 **Size Optimized**: Exports within strict size limits (≤2MB PNG, ≤2 sprite sheets, ≤5KB JSON)
- 🦴 **Spine Compatible**: Full support for bones, slots, attachments, and transforms
- 🎮 **Slot-Game Ready**: Optimized for slot game requirements and performance

## Tech Stack

- **Desktop Shell**: Electron + Vite
- **Node Graph**: Rete.js v2
- **Preview**: PixiJS v8 + pixi-particles + @pixi-spine
- **Asset Packing**: maxrects-pali

## Getting Started

### Prerequisites

- Node.js ≥20
- pnpm (recommended) or npm

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sparcle.git
cd sparcle

# Install dependencies
pnpm install
```

### Development

```bash
# Start in development mode
pnpm dev

# Run Electron app in dev mode
pnpm electron:dev

# Run tests
pnpm test
```

### Building

```bash
# Build for production
pnpm build

# Package Electron app
pnpm package
```

## Project Structure

```
/sparcle
 ├─ /src
 │   ├─ main/                  # Electron main process
 │   ├─ renderer/
 │   │    ├─ graph/           # Rete nodes & controls
 │   │    └─ preview/         # Pixi canvas + runtime
 │   ├─ core/
 │   │    ├─ ir.ts           # IR types & helpers
 │   │    ├─ compiler.ts     # IR → Spine JSON
 │   │    ├─ loop.ts         # looping utils
 │   │    └─ optimiser.ts    # key decimation
 │   └─ cli/
 └─ /examples
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Rete.js](https://github.com/retejs/rete) - Node graph system
- [PixiJS](https://pixijs.com) - 2D rendering engine
- [pixi-spine](https://github.com/pixijs/spine) - Spine runtime
- [maxrects-pali](https://github.com/jamiefoo/maxrects-pali) - Texture packing
