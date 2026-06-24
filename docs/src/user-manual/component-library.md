# Component Library

Save any multi-selected region as a reusable component, then re-instantiate it anywhere with fresh wire IDs.

## Saving a component

1. Shift+click the blocks and pins you want to include (wires between them are captured automatically).
2. `File > Save Selection as Component...` — enter a name.
3. The component appears as a button in the **Components** expander in the left panel.

## Instantiating a component

Click the component button in the Components expander. A fresh copy is placed on the canvas at a slightly shifted position, with new UUIDs for all elements so it doesn't interfere with the original.

A **Refresh** button rescans `src/components/` in case you added files externally.

## Storage

Components are stored as JSON files in `src/components/`. You can share or version-control them alongside your project.
