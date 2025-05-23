# Sparcle Project Journey Summary

This document summarizes the development progress, key decisions, and challenges encountered during the Sparcle project up to the decision to revert to Sprint 3 and explore a Python-based reimplementation.

## Initial Context & Flowcharting
*   The project began by establishing its current state and architecture.
*   Technology Stack: Electron, Vite, Rete.js (for the node graph), and PixiJS (for rendering).
*   A key file, `SparcleFlowChart.ini`, was created, outlining:
    *   Project goals
    *   Tech stack
    *   Architecture (PNGs -> Assets DB -> Atlas Packer; Nodes UI -> Rete Graph -> IR -> Spine Compiler -> JSON/Atlas/PNG, with a Live Preview via Pixi)
    *   Looping algorithm concept
    *   Directory structure
    *   A 6-sprint milestone plan.
*   The project was determined to be in **Sprint 3**, focusing on defining the Intermediate Representation (IR) and exporting non-looping Spine bursts at that stage.

## Moving to GitHub
*   The project was successfully initialized as a Git repository and pushed to a private GitHub repository: `https://github.com/canahmet-git2/Sparcle`.
*   Steps included: `git init`, `add`, `commit`, remote repository creation, `git remote add origin`, `branch -M main`, and `git push -u origin main`.
*   A push conflict (due to existing remote content) was resolved by pulling and then pushing again.

## Sprint 4: Looping Algorithm Implementation
*   The project proceeded to Sprint 4, focusing on implementing the Looping Algorithm.
*   **Core Logic:**
    *   `src/core/loop.ts`: Introduced `ParticleLoopOptimizer` class (handling pre-warming, transform sampling, keyframe optimization, loop continuity).
    *   `src/core/loop.test.ts`: Unit tests for the loop optimizer.
*   **Integration:**
    *   `src/core/particle/ParticleNodeSystem.ts`: Updated with `enableLooping`, `disableLooping`, and `applyLoopTransforms` methods.
*   **UI:**
    *   `src/renderer/graph/nodes/OutputNode.tsx`: Updated to control loop duration and trigger updates in the particle system.
*   **Types:**
    *   `src/types/global.d.ts`: Added a global TypeScript declaration for `window.particleSystem`.

## Visual Testing of Looping
*   A test scene was created to visually verify the looping functionality:
    *   `src/examples/loop-test.ts`: Implemented a circular particle motion and color transition.
    *   `src/examples/LoopTest.tsx`: A React component to display the test scene.
*   This test page was added as a route (`/loop-test`) in `src/renderer/App.tsx`.
*   The development server (`npm run dev`) was started, initially encountering a 500 error due to incorrect CSS import paths in `App.tsx`, which was subsequently fixed.

## Troubleshooting `npm run dev` and `npm test`
This phase involved significant troubleshooting:

*   **`npm run dev` Issues:**
    *   No console output: Checked `package.json` and `vite.config.ts`. Uncommented Vite server config and set port to 5173.
    *   `Failed to fetch dynamically imported module` for `react-router-dom`: An attempt to install a specific version was rejected by the user.
*   **Jest Test Failures (`npm test`):**
    *   **`ts-jest` and `moduleResolution` Conflict:**
        *   `tsconfig.json`'s `"moduleResolution": "bundler"` was incompatible with `ts-jest` v29.
        *   **Solution:** Created `tsconfig.jest.json` with `"moduleResolution": "nodenext"` and updated `jest.config.js` to use this new tsconfig and the `ts-jest/presets/default-esm` preset.
    *   **`nvm` and Environment Issues:**
        *   User guided to ensure Node 20 LTS was active using `nvm`.
        *   Persistent errors where `npm` (and later `node`) was "not recognized" by the tool's `run_terminal_cmd`, despite working in the user's manually opened terminal. This indicated PATH or `nvm` shim issues within the tool's execution environment.
    *   **Code Errors & Fixes:**
        *   Typo (`es{`) at the beginning of `tsconfig.json` fixed.
        *   `Property 'getNodes' does not exist on type 'ParticleNodeSystem'`: Method added.
        *   Unused variable `lastFrame` in `src/core/loop.ts`: Removed.
        *   Mocking issues in `NodeParticleRenderer.test.ts`: Switched to `jest.spyOn`.
        *   Unused `React` import in `Vector2Input.test.tsx`: Removed.
        *   `'container' is possibly 'undefined'` in `NodeParticleRenderer.test.ts`: Added an `expect(container).toBeDefined();` check.
        *   Type assertion for `(PIXI.Sprite as jest.Mock)`: Changed to `(PIXI.Sprite as unknown as jest.Mock)`.
    *   **PixiJS v8 Texture API Change:**
        *   Error: `PIXI.Texture.WHITE.clone is not a function` (initial error was a type error with `Texture.from(Texture.WHITE)`).
        *   PixiJS v8 changed `Texture.from()` to no longer accept another `Texture` instance.
        *   Recommended fix: Change `PIXI.Texture.from(PIXI.Texture.WHITE)` to `PIXI.Texture.WHITE.clone()` in `src/core/particle/NodeParticleRenderer.ts`.
        *   Test mock for `PIXI.Texture.WHITE` in `NodeParticleRenderer.test.ts` was updated multiple times to correctly provide a `clone` method.
    *   **Jest Configuration:**
        *   Updated `jest.config.js` to use the new `transform` array form for `ts-jest` to silence a deprecation warning about `globals`.

## Current Status (Prior to Revert)
*   Code changes for Sprint 4 and subsequent fixes remained uncommitted.
*   Persistent issues with the tool's terminal not recognizing `npm`/`node` commands correctly, despite them working in the user's local terminal.
*   The decision was made to revert to the "Sprint 3" commit (`6acd65c`) and explore a Python-based approach. 

## Pivot to Python/Kivy and Restarting Sprint Cycle

Following the challenges with the JavaScript-based stack and the decision to explore a Python-based solution, the project pivoted to using Python with the Kivy framework. This change aligns with the `sparcleflowchart.ini`'s alternative tech stack proposal.

*   **New Technology Stack Focus:** Python, Kivy.
*   **Project Reset:** Development effectively restarted, adhering to the Kivy-focused sprint plan outlined in `sparcleflowchart.ini`.

### Sprint 1 (Kivy Foundation & Core UI Shell) - Python
*   **Status:** COMPLETE
*   **Key Activities:**
    *   Set up the Kivy project structure.
    *   Designed the main window layout with placeholders for Node Editor, Timeline, Parameters Panel, and Preview area. (Conceptual, code for placeholders established).
    *   Implemented a basic Kivy App structure (`main.py`, `src/app/main_app.py`).
    *   Created UI placeholder widgets in `src/ui/` for different sections of the application.
    *   Basic menu bar (conceptual, placeholder in Kivy structure).
    *   Research into Kivy node editor and timeline solutions indicated a preference for custom implementations or heavily adapted garden components.
    *   Initial version of the **Effect IR** (`src/core/ir.py`) was developed, including `EmitterProperties`, `AnimatedParameter`, `TimelineKeyframe`, and `EffectIR` (as an `EventDispatcher`). This handles basic parameter storage, animation data structures, and value retrieval at specific times, including interpolation.

### Sprint 2 (Node Editor - Phase 1 - Basic Functionality) - Python
*   **Status:** IN PROGRESS
*   **Current Focus:** Defining Python class structures for nodes (`src/core/nodes.py`) and parameters (partially addressed in `ir.py`).
    *   Task 2.1: Implement basic node creation (e.g., Source, Display nodes).
    *   Task 2.4: Define Python class structure for nodes/parameters.
*   **Next Steps:**
    *   Node dragging & selection (Task 2.2).
    *   Basic connection drawing (sockets) (Task 2.3).

---
*Last Updated: (Current Date)* 