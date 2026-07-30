# Controller Architecture

## Purpose

The controller contains the complete business logic of the KNX Scene
Cycler. It translates KNX telegrams into Home Assistant actions while
updating the runtime.

The controller is the only component that interprets KNX scene numbers.

## Responsibilities

The controller shall:

-   Receive KNX telegrams
-   Resolve KNX scene numbers
-   Activate Home Assistant scenes
-   Handle neutral scene switching
-   Update runtime
-   Trigger LED updates
-   Notify entities through the runtime

Configuration, runtime storage and UI entities must not duplicate this
logic.

------------------------------------------------------------------------

# Processing Flow

``` text
KNX Telegram
      │
      ▼
Scene Number
      │
      ▼
Scene Mapping Lookup
      │
      ▼
SceneMapping
      │
      ├───────────────┐
      │               │
      ▼               ▼
Regular         Neutral
      │               │
      ▼               ▼
Activate HA     Deactivate
Scene           Runtime
      │               │
      └──────┬────────┘
             ▼
      Update Runtime
             ▼
        Update LED
```

## Lookup Strategy

The controller never searches by slot.

The primary lookup is:

-   KNX scene number → SceneMapping

The lookup is built from the configuration and provides constant-time
access.

## Regular Scene

For a regular mapping the controller:

1.  Resolves the mapping.
2.  Activates the configured Home Assistant scene.
3.  Stores the current scene number.
4.  Stores the last regular scene number.
5.  Updates the LED.

## Neutral Scene

For the neutral mapping the controller:

1.  Resolves the mapping.
2.  Activates the configured neutral Home Assistant scene.
3.  Marks the runtime inactive.
4.  Keeps the last regular scene number unchanged.
5.  Updates the LED.

## Toggle Behaviour

The toggle operation alternates between:

-   neutral scene
-   last regular scene

The controller never guesses a scene. It always restores the last
recorded regular KNX scene number.

## Error Handling

The controller should ignore:

-   unknown scene numbers
-   duplicate telegrams with no state change

Configuration errors should raise explicit exceptions during validation
rather than at runtime.

## Design Principles

-   Business logic belongs only to the controller.
-   Runtime stores state only.
-   Config stores configuration only.
-   UI entities present state only.
-   ETS defines transmitted scene numbers.
-   Home Assistant defines the meaning of each scene number.

## Future Extensions

The architecture is designed to support:

-   up to 64 KNX scene mappings
-   Options Flow editing
-   LED colour extensions
-   additional KNX objects
-   persistent runtime restoration
