# Configuration Flow Architecture

## Purpose

The Config Flow guides the user through creating a logical KNX Scene
Cycler button. Its responsibility is to collect configuration only.
Business logic belongs to the controller.

## Initial Configuration

Each button requires:

-   Device name
-   KNX scene selection group address
-   KNX switch group address
-   KNX status LED group address

After the communication objects are configured, the user creates the
scene mappings.

## Required Scene Mappings

The initial configuration requires:

-   At least four regular scene mappings
-   Exactly one neutral scene mapping

Each mapping contains:

-   Display name
-   KNX scene number (1--64)
-   Home Assistant scene
-   LED colour value (0--255)
-   Neutral flag

## Validation

The Config Flow validates:

-   Unique KNX scene numbers
-   Unique mapping identifiers
-   Exactly one neutral mapping
-   At least four regular mappings
-   Maximum of 64 mappings
-   Valid LED colour range

## Separation of Responsibilities

### ETS

The ETS project determines which KNX scene numbers are sent by the push
button.

### Home Assistant

The integration assigns a meaning to each configured KNX scene number.

This separation allows ETS programming to change independently from the
Home Assistant configuration.

## Options Flow (Future)

The Options Flow will support:

-   Add mapping
-   Edit mapping
-   Remove mapping
-   Reorder mappings
-   Change LED colour values
-   Rename mappings

## Design Principles

-   Collect configuration only.
-   Do not contain controller logic.
-   Do not duplicate runtime state.
-   Keep the workflow extensible for future releases.
