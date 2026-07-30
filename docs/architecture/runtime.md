# Runtime Architecture

## Purpose

The runtime stores the mutable state of a logical KNX Scene Cycler
button. It contains only transient information and must never duplicate
configuration.

## Responsibilities

The runtime is responsible for:

-   Current button state
-   Currently active KNX scene number
-   Last active regular KNX scene number
-   Runtime listeners
-   Availability state

## Button States

  State         Description
  ------------- -------------------------------------
  INACTIVE      Neutral scene is active.
  ACTIVE        A regular scene is active.
  UNAVAILABLE   Runtime is temporarily unavailable.

## Stored Runtime Values

### current_scene_number

The KNX scene number currently considered active.

### last_regular_scene_number

The last activated regular scene.

This value is intentionally preserved while the neutral scene is active,
allowing the controller to return to the previous regular scene.

## Listener Model

The runtime exposes a listener mechanism.

Whenever the runtime changes, all registered listeners are notified.

Typical listeners:

-   Select entity
-   Switch entity
-   Future diagnostics

## Migration Strategy

During the migration from slot-based processing to scene-number
processing, legacy slot accessors may temporarily remain available as
compatibility helpers.

No new functionality should depend on slot numbers.

## Design Principles

-   Runtime stores state only.
-   Configuration belongs to SceneButtonConfig.
-   Business logic belongs to the controller.
-   ETS remains responsible for transmitted KNX scene numbers.
-   Runtime never interprets KNX telegrams.

## Future Work

-   Remove remaining slot compatibility.
-   Restore runtime state after Home Assistant restart.
-   Support extended diagnostics if required.
