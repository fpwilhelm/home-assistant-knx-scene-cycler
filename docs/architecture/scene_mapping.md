# Scene Mapping Architecture

## Status

This document describes the target architecture of the KNX Scene Cycler
integration after the ongoing scene mapping refactoring.

## Design Goals

-   Decouple ETS configuration from Home Assistant scene handling.
-   Support up to 64 KNX scene numbers.
-   Treat regular scene mappings equally.
-   Represent the neutral scene as a normal mapping with
    `is_neutral = true`.
-   Keep the implementation extensible for future Options Flow support.

## Responsibilities

### ETS

The KNX installer decides which KNX scene numbers are transmitted by the
push button.

### Home Assistant Integration

The integration assigns meaning to each KNX scene number by mapping it
to:

-   Home Assistant scene
-   LED colour value
-   Display name
-   Neutral flag

## SceneMapping

Each configured mapping contains:

-   mapping_id
-   name
-   knx_scene_number
-   scene_entity_id
-   led_color_value
-   is_neutral

Exactly one mapping must be marked as neutral.

## SceneButtonConfig

A button configuration contains:

-   device_name
-   ga_scene_select
-   ga_switch
-   ga_status_led
-   scene_mappings

The configuration also provides a runtime lookup by KNX scene number.

## Runtime

Runtime stores:

-   current_scene_number
-   last_regular_scene_number

Slots are retained only temporarily for migration compatibility.

## Controller

Processing flow:

1.  Receive KNX scene number.
2.  Resolve SceneMapping.
3.  Activate Home Assistant scene.
4.  Update runtime.
5.  Send LED status if configured.

## Validation

-   Maximum 64 mappings.
-   At least four regular mappings.
-   Exactly one neutral mapping.
-   Unique mapping IDs.
-   Unique KNX scene numbers.

## Future Work

-   Rewrite controller for scene-number based processing.
-   Remove remaining slot compatibility.
-   Rewrite Config Flow.
-   Implement Options Flow for adding, editing and deleting mappings.
