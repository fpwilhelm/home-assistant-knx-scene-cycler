# Architecture

## KNX Scene Cycler

The **KNX Scene Cycler** is a Home Assistant custom integration for connecting KNX scene buttons with existing Home Assistant scenes.

The integration allows one logical hub to contain multiple independently configurable scene buttons. Each button listens to its own KNX group addresses, maps KNX scene numbers to Home Assistant scenes, provides dashboard entities, and manages its own active state.

---

## 1. Purpose

Many KNX push-button interfaces can cycle through scene numbers but cannot directly activate Home Assistant scenes.

The KNX Scene Cycler bridges this gap:

```text
KNX push button
    ↓
KNX scene number
    ↓
KNX Scene Cycler
    ↓
Mapped Home Assistant scene
```

Each configured button supports:

- four regular Home Assistant scenes,
- one neutral/off Home Assistant scene,
- a KNX group address for scene selection,
- a KNX group address for toggle control,
- an optional KNX group address for a status LED,
- direct control through Home Assistant,
- restoration of the last regular scene.

---

## 2. Terminology

### Hub

A **Hub** is the top-level Home Assistant configuration entry.

It acts as a logical container for one or more scene buttons.

A hub does not execute scene logic itself.

Example:

```text
KNX Scene Cycler
└── Living Room
```

### Button

A **Button** represents one physical KNX scene-control function.

Each button has its own:

- persistent internal identifier,
- user-defined name,
- KNX group addresses,
- scene-number mappings,
- neutral/off scene,
- active state,
- last active regular scene.

Example:

```text
Living Room
├── Left scene button
├── Right scene button
└── TV scene button
```

The term **Button** refers to a logical scene controller and not to a Home Assistant `button` entity.

### Regular scene

A **regular scene** is one of the four Home Assistant scenes that can be selected by a KNX scene number.

Regular scenes represent the active states of a button.

### Neutral/off scene

The **neutral/off scene** is activated when the button is switched off.

It is not part of the four KNX scene-number mappings and is not stored as the last active regular scene.

### Last active scene

The **last active scene** is the most recently activated regular scene.

It is used when the button is switched back on after the neutral/off scene was active.

---

## 3. Functional model

The integration uses the following hierarchy:

```text
KNX Scene Cycler integration
└── Hub
    ├── Button 1
    │   ├── Switch entity
    │   └── Select entity
    ├── Button 2
    │   ├── Switch entity
    │   └── Select entity
    └── Button n
        ├── Switch entity
        └── Select entity
```

Each button operates independently.

A KNX telegram received for one button must never modify the state of another button unless both buttons intentionally use the same Home Assistant scene.

---

## 4. KNX communication

Each button uses up to three KNX group addresses.

| Function | Direction | Data | Required |
|---|---|---|---|
| Scene selection | KNX → Home Assistant | Scene number, DPT 17.001 | Yes |
| Toggle control | KNX → Home Assistant | Value `0` | Yes |
| Status LED | Home Assistant → KNX | Value `0` or `1` | No |

### 4.1 Scene-selection group address

Example:

```text
31/0/20
```

The physical KNX button sends a scene number using DPT 17.001.

The integration listens for `knx_event` events whose destination matches the configured group address.

The received value is compared with the four scene numbers configured for the button.

Example mapping:

| Slot | KNX scene number | Home Assistant scene |
|---|---:|---|
| Scene 1 | 1 | `scene.living_room_bright` |
| Scene 2 | 2 | `scene.living_room_relax` |
| Scene 3 | 3 | `scene.living_room_tv` |
| Scene 4 | 4 | `scene.living_room_reading` |

The scene numbers are configurable and may use any valid value supported by the integration.

The integration must not silently add or subtract `1` from the KNX event value. The value exposed by the Home Assistant KNX event is compared directly with the configured value.

### 4.2 Toggle group address

Example:

```text
31/0/21
```

The physical KNX button sends the value `0` for every long press.

The value is interpreted as a toggle impulse rather than as an explicit off command.

The action depends on the current logical state:

```text
Current state active
→ activate neutral/off scene
→ change state to inactive

Current state inactive
→ restore last active regular scene
→ change state to active
```

Values other than `0` are ignored.

### 4.3 Status-LED group address

Example:

```text
31/0/22
```

The status-LED group address is optional.

The integration sends:

```text
1 = one of the four regular scenes is active
0 = the neutral/off scene is active
```

The status LED represents the logical state of the scene button. It does not indicate which of the four regular scenes is active.

No KNX status telegram is sent when no status-LED group address has been configured.

---

## 5. Scene-selection behavior

When the integration receives a valid configured scene number:

1. The mapped Home Assistant scene is activated.
2. The selected regular scene becomes the last active scene.
3. The logical state becomes active.
4. The Home Assistant switch entity becomes on.
5. The Home Assistant select entity shows the selected scene.
6. The value `1` is sent to the optional status-LED group address.

Example:

```text
KNX event:
destination = 31/0/20
value = 3

Configured mapping:
3 → scene.living_room_tv

Result:
scene.living_room_tv is activated
last active scene = scene.living_room_tv
button state = active
status LED = 1
```

### Unknown scene numbers

If a scene number is received that is not mapped to one of the four configured scenes:

- no Home Assistant scene is activated,
- the active state is not changed,
- the last active scene is not changed,
- no status-LED telegram is sent,
- a debug log entry may be created.

This is not treated as a fatal integration error.

---

## 6. Toggle behavior

### 6.1 Switching off

When the button is active and receives a valid toggle impulse:

1. The neutral/off Home Assistant scene is activated.
2. The previous regular scene remains stored as the last active scene.
3. The logical state becomes inactive.
4. The Home Assistant switch entity becomes off.
5. The value `0` is sent to the optional status-LED group address.

The select entity continues to represent the last selected regular scene. It does not change to the neutral/off scene.

### 6.2 Switching on

When the button is inactive and receives a valid toggle impulse:

1. The last active regular scene is activated.
2. The logical state becomes active.
3. The Home Assistant switch entity becomes on.
4. The select entity shows the restored regular scene.
5. The value `1` is sent to the optional status-LED group address.

### 6.3 Fallback behavior

If no valid last active scene is available, Scene 1 is used as the fallback.

This may occur:

- after the first installation,
- after invalid restored state data,
- after a previously configured scene has been removed,
- after configuration migration.

The fallback scene then becomes the new last active scene.

---

## 7. Home Assistant entities

Each configured button creates two Home Assistant entities.

### 7.1 Switch entity

The switch represents whether a regular scene or the neutral/off scene is active.

```text
on  = one of the four regular scenes is logically active
off = the neutral/off scene is logically active
```

#### Turning the switch off

When the switch is turned off from Home Assistant:

1. The neutral/off scene is activated.
2. The last regular scene remains stored.
3. The logical state becomes inactive.
4. The status LED receives `0`, when configured.

#### Turning the switch on

When the switch is turned on from Home Assistant:

1. The last active regular scene is restored.
2. Scene 1 is used if no valid last active scene exists.
3. The logical state becomes active.
4. The status LED receives `1`, when configured.

The switch must call the shared button controller directly. It must not locate or control another entity by constructing an entity ID.

### 7.2 Select entity

The select entity allows direct selection of one of the four regular scenes.

Selecting an option:

1. activates the corresponding Home Assistant scene,
2. stores it as the last active scene,
3. changes the logical state to active,
4. updates the switch entity,
5. sends `1` to the optional status-LED group address.

The neutral/off scene is not offered as a select option. It is controlled through the switch or the KNX toggle group address.

The select options should use stable, user-friendly labels. The entity must internally map those labels to the configured scene slots and scene entity IDs.

---

## 8. Shared runtime controller

Each button has exactly one shared runtime controller.

Suggested class name:

```python
SceneButtonController
```

The controller owns all state and behavior for one button.

Responsibilities include:

- receiving and evaluating KNX events,
- mapping KNX scene numbers,
- activating Home Assistant scenes,
- handling toggle impulses,
- managing active/inactive state,
- storing the last active regular scene,
- sending the status-LED value,
- notifying associated Home Assistant entities,
- validating restored state.

The switch and select entities do not maintain independent scene states.

They delegate all actions to the same controller:

```python
await controller.activate_scene(scene_slot)
await controller.turn_on()
await controller.turn_off()
await controller.toggle()
```

This prevents state divergence between:

- KNX control,
- the Home Assistant switch,
- the Home Assistant select.

---

## 9. Runtime state

Each button controller maintains at least:

```text
is_active
last_active_scene_slot
```

Suggested representation:

```python
is_active: bool
last_active_scene_slot: int
```

The last active scene should be stored as a stable scene slot or another configuration-independent identifier, rather than only as a display label.

Valid regular scene slots are:

```text
1
2
3
4
```

The neutral/off scene is not stored as `last_active_scene_slot`.

---

## 10. State restoration

The integration must preserve the logical state across Home Assistant restarts and integration reloads without requiring manually created helpers.

The previous blueprint used:

- an `input_text` helper for the last active scene,
- an `input_boolean` helper for the active state.

The custom integration replaces these helpers with Home Assistant state restoration.

The following state should be restored:

- active or inactive,
- last active regular scene.

### Restart behavior

After a Home Assistant restart or integration reload:

- the integration restores its internal logical state,
- it does not automatically activate a Home Assistant scene,
- it does not automatically send a status-LED telegram solely because of restoration,
- the restored last scene is used on the next explicit turn-on or toggle action.

This avoids unexpected scene activation during startup.

If restored data is missing or invalid:

```text
is_active = false
last_active_scene_slot = 1
```

The exact default active state may later become configurable, but the initial implementation uses the safe inactive state.

---

## 11. Persistent configuration model

A hub is represented by one Home Assistant config entry.

Each button should be stored as an independently manageable configuration item, preferably using Home Assistant config subentries when supported by the target Home Assistant version.

Conceptual configuration:

```yaml
hub:
  name: "Living Room"

buttons:
  - id: "a stable generated identifier"
    name: "Left scene button"

    knx:
      scene_selection_address: "31/0/20"
      toggle_address: "31/0/21"
      status_led_address: "31/0/22"

    scenes:
      - slot: 1
        knx_scene_number: 1
        entity_id: "scene.living_room_bright"

      - slot: 2
        knx_scene_number: 2
        entity_id: "scene.living_room_relax"

      - slot: 3
        knx_scene_number: 3
        entity_id: "scene.living_room_tv"

      - slot: 4
        knx_scene_number: 4
        entity_id: "scene.living_room_reading"

    neutral_scene:
      entity_id: "scene.living_room_off"
```

This YAML illustrates the model only. The configuration is stored through Home Assistant config entries and is not intended as a user-maintained YAML configuration.

---

## 12. Stable button identity

Every button receives a generated persistent identifier when it is created.

Example:

```text
e0d570ef0f414c4ca5feb63ea81132cf
```

The identifier must not depend on:

- the button name,
- its position in a list,
- a KNX group address,
- an entity ID,
- the order in which buttons are loaded.

Renaming, editing, adding, deleting, or reordering other buttons must not change an existing button identifier.

Suggested entity unique IDs:

```text
<config_entry_id>_<button_id>_switch
<config_entry_id>_<button_id>_scene_select
```

Example:

```text
01J..._e0d570ef0f414c4ca5feb63ea81132cf_switch
01J..._e0d570ef0f414c4ca5feb63ea81132cf_scene_select
```

---

## 13. Device and entity association

The hub and its buttons should be represented clearly in the Home Assistant device registry.

Preferred model:

```text
Integration
└── Hub device
    ├── Button 1 switch
    ├── Button 1 scene select
    ├── Button 2 switch
    └── Button 2 scene select
```

A later version may represent every logical button as a separate child device if this provides a better Home Assistant user experience.

For the initial implementation, all button entities may belong to the hub device while retaining their stable button identifiers.

Entity names should include the user-defined button name.

Example:

```text
Living Room – Left scene button
├── Active
└── Scene
```

The exact naming model must avoid generating entity IDs in code for communication between entities.

---

## 14. Configuration flow

### 14.1 Creating a hub

The initial config flow creates the hub.

Required input:

- hub name.

The initial flow may also offer creation of the first button, but the hub must remain valid even when it temporarily contains no buttons.

### 14.2 Creating a button

The button creation flow requests:

- button name,
- scene-selection group address,
- toggle group address,
- optional status-LED group address,
- Home Assistant scene for Scene 1,
- KNX scene number for Scene 1,
- Home Assistant scene for Scene 2,
- KNX scene number for Scene 2,
- Home Assistant scene for Scene 3,
- KNX scene number for Scene 3,
- Home Assistant scene for Scene 4,
- KNX scene number for Scene 4,
- neutral/off Home Assistant scene.

### 14.3 Managing buttons

The user must be able to:

- add a button,
- edit an existing button,
- delete a button.

Editing a button must retain its persistent identifier.

Deleting a button must remove its runtime controller and associated entities after the integration is reloaded.

Deleting one button must not change the identity or state of any other button.

---

## 15. Validation rules

### 15.1 Button name

The button name:

- is required,
- must not contain only whitespace,
- should be unique within the same hub.

### 15.2 KNX group addresses

Required group addresses:

- must use valid KNX group-address syntax,
- must not be empty,
- must not be identical within the same button.

The status-LED address is optional.

A warning or validation error should be shown when group addresses conflict with another button in the same hub.

At minimum, duplicate input addresses must not be accepted silently.

### 15.3 KNX scene numbers

Each of the four KNX scene numbers:

- must be within the supported scene-number range,
- must be unique within the same button.

No two regular scene slots of one button may use the same KNX scene number.

### 15.4 Home Assistant scenes

Each configured entity must belong to the `scene` domain.

All five scene selections are required in the initial implementation:

- four regular scenes,
- one neutral/off scene.

The same Home Assistant scene may technically be reused, although the configuration flow may warn that this is usually not useful.

### 15.5 Optional status LED

An empty status-LED field means that status feedback is disabled.

No KNX write operation is attempted in this case.

---

## 16. Event processing

The integration registers a listener for Home Assistant `knx_event` events.

Incoming events are routed to the correct button controller based on the destination group address.

Conceptual routing:

```text
KNX event
    ↓
Destination address lookup
    ↓
Matching button controller
    ↓
Scene-selection handler or toggle handler
```

The event listener should be registered centrally per config entry rather than independently by every entity.

The config-entry runtime data should contain:

- button controllers by button ID,
- lookup table for scene-selection addresses,
- lookup table for toggle addresses,
- unsubscribe callbacks.

Example:

```python
controllers_by_id: dict[str, SceneButtonController]
scene_address_map: dict[str, SceneButtonController]
toggle_address_map: dict[str, SceneButtonController]
```

All event listeners must be removed when the config entry is unloaded.

---

## 17. Concurrency and repeated events

Actions for one button must be serialized to avoid overlapping scene activations.

A controller-level lock should prevent race conditions such as:

```text
KNX scene-selection event
and
Home Assistant switch action
arriving simultaneously
```

Actions for different buttons should remain independent.

Repeated valid events are processed normally.

A repeated selection of the already selected regular scene may activate the Home Assistant scene again. This is intentional because Home Assistant scenes may need to reapply their configured state.

---

## 18. Error handling

A failed Home Assistant scene activation must not crash the integration.

Expected behavior:

- log the error,
- do not report a successful state transition,
- do not update the last active scene,
- do not send a successful status-LED value.

A failed KNX status-LED write should:

- be logged,
- not undo a successfully activated Home Assistant scene,
- not make the button entity unavailable.

Malformed or incomplete KNX events should be ignored safely.

The integration must not expose unhandled exceptions through the config flow or options flow.

---

## 19. Logging

Recommended logging levels:

### Debug

- received KNX destination and value,
- matched button identifier,
- resolved scene slot,
- ignored unmapped scene number,
- restored internal state.

### Info

- important configuration migrations,
- unrecoverable button configuration skipped during setup.

### Warning

- configured Home Assistant scene no longer exists,
- duplicate runtime address detected,
- invalid restored state replaced with fallback.

### Error

- Home Assistant scene activation failed,
- KNX status write failed,
- config entry cannot be set up.

Routine KNX telegrams should not create info-level log noise.

---

## 20. Translation and user interface

All user-facing strings must use Home Assistant translation resources.

Required files include:

```text
custom_components/knx_scene_cycler/strings.json
custom_components/knx_scene_cycler/translations/de.json
```

Python code must not contain final user-facing labels for:

- config-flow fields,
- descriptions,
- error messages,
- menu actions,
- abort reasons.

The development source language is English. German is provided through translation resources.

---

## 21. Configuration migration

The existing prototype stores one or more button configurations in the config entry using the previous `functions` list.

The refactored integration must either:

1. provide an explicit migration to the new data model, or
2. document that prototype config entries must be removed and recreated.

Until a reliable migration exists, the integration version must remain below `1.0.0`.

No automatic migration should guess missing persistent button identifiers without storing the generated identifiers permanently.

---

## 22. Out of scope for the initial refactor

The following features are not required for the first stable architecture:

- more than four regular scenes per button,
- dynamic scene-slot counts,
- sending DPT 17.001 scene commands back to KNX,
- scene-learning or scene-saving commands,
- automatic detection of KNX group addresses,
- importing an ETS project,
- synchronizing the status LED from external light states,
- verifying whether a Home Assistant scene still matches the real device states,
- multiple neutral/off scenes,
- configurable LED payloads other than `0` and `1`.

These features may be considered after the multi-button architecture is stable.

---

## 23. Initial acceptance criteria

The architecture is considered functional when all of the following tests succeed.

### Configuration

- A hub can be created.
- The first button can be created.
- A second button can be added without an internal server error.
- Existing buttons can be edited.
- Existing buttons can be deleted.
- Restarting Home Assistant retains all configured buttons.
- Deleting the first button does not change the identity of the second button.

### KNX scene selection

- Button 1 reacts only to its configured scene-selection address.
- Button 2 reacts only to its configured scene-selection address.
- Each of the four configured KNX scene numbers activates the correct Home Assistant scene.
- Unknown scene numbers are ignored.
- Selecting a regular scene marks only the matching button as active.
- Selecting a regular scene stores it as the last active scene.
- The optional status LED receives `1`.

### KNX toggle

- A long press while active activates the neutral/off scene.
- A long press while inactive restores the last regular scene.
- The toggle value must be `0`.
- The optional status LED receives `0` while inactive.
- The optional status LED receives `1` after restoration.

### Home Assistant switch

- Turning the switch off activates the neutral/off scene.
- Turning the switch on restores the last regular scene.
- Scene 1 is used as fallback when no valid last scene is available.
- The KNX status LED follows the switch state.

### Home Assistant select

- Selecting any of the four options activates the corresponding scene.
- The selected scene becomes the last active scene.
- The associated switch becomes on.
- No entity ID is constructed or guessed to synchronize the entities.

### Restart and reload

- A restart restores the last active scene reference.
- A restart restores the logical active state.
- No scene is activated automatically during startup.
- No duplicate KNX event listeners remain after a reload.
- Every KNX event causes at most one action per matching button.

---

## 24. Implementation order

The refactor should be implemented in the following order:

1. Constants and typed configuration model.
2. Persistent button identifiers.
3. Hub and button configuration flow.
4. Translation resources.
5. Button add, edit, and delete lifecycle.
6. Shared runtime controller.
7. Switch entity.
8. Select entity.
9. Central KNX event routing.
10. Status-LED output.
11. State restoration.
12. Configuration migration or documented reset.
13. Automated tests.
14. Documentation and release preparation.

This order keeps configuration, runtime logic, and KNX communication clearly separated and allows each layer to be tested before the next one is introduced.