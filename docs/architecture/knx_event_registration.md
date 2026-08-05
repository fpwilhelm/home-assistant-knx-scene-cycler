# KNX Event Registration

Part of the KNX Scene Cycler Architecture Documentation.

Related documents:

- Architecture Overview
- Controller
- Runtime
- Trigger Modes

---

# Purpose

KNX Scene Cycler registers the group addresses configured by the user with the
Home Assistant KNX integration.

Users must not have to repeat these addresses in `knx.yaml` or
`configuration.yaml` merely to make Home Assistant emit `knx_event` events.

ETS remains responsible for programming the physical KNX installation,
coupler filter tables and KNX Secure assignments.

---

# Responsibilities

The KNX Event Registration Manager is responsible for:

- Registering configured input group addresses through `knx.event_register`
- Reference-counting shared registrations across Config Entries
- Removing a registration only after its final integration user is unloaded
- Keeping scene and toggle address decoding unambiguous

The Hub is responsible for:

- Owning one Home Assistant `knx_event` listener per Config Entry
- Routing a received group address to every matching Scene Button Controller
- Allowing multiple Scene Buttons to share a group address
- Coordinating KNX status LED writes after incoming events
- Sending scene-number feedback after restoring from Neutral Scene mode

Entities are not responsible for KNX event registration or event routing.

---

# Registered Addresses

The integration registers only addresses from which it expects input:

- Every Scene Button scene selection group address
- Every Separate Toggle group address

Status LED addresses are output-only and are not registered as event inputs.

Scene selection addresses are registered with the KNX `scene_number` value
type. Toggle addresses use their binary raw value.

Only incoming `GroupValueWrite` telegrams are routed to controllers. Outgoing
feedback, GroupValueRead requests and GroupValueResponse telegrams are ignored
as control input.

---

# Shared Group Addresses

One scene selection group address may be used by multiple Scene Buttons.

Every telegram received for that address is routed to every matching
controller. Each controller independently ignores scene numbers that are not
part of its configuration.

This supports configurations such as:

```text
31/0/200
├── Scene Button 1: scene numbers 2, 3, 4, 5
└── Scene Button 2: scene numbers 6, 7, 8, 9
```

Shared registrations are reference-counted across all KNX Scene Cycler Config
Entries. Removing or editing one Scene Button must not remove a registration
that is still required elsewhere.

A group address must not be used as a scene selection address and a toggle
address at the same time. Those roles require different payload semantics and
would make event decoding ambiguous.

---

# Scene Cycle Feedback

Some physical KNX scene buttons use a status communication object to track the
last scene number on their scene selection group address.

In Neutral Scene mode, a long press sends raw KNX scene value 0, represented
by Home Assistant as scene number 1. This can reset the physical button's
internal scene cycle.

When a second Neutral Scene telegram restores the last regular scene, the Hub
sends that regular scene number to the scene selection group address. A
physical status object can then synchronize its internal cycle before the next
short press.

The feedback is sent as KNX `scene_number` data and is ignored by the Hub's
incoming-event filter.

---

# Lifecycle

```text
Config Entry setup
        │
        ├── Collect unique scene and toggle input addresses
        ├── Acquire registrations
        ├── Register one Config Entry event listener
        └── Start entity platforms

Config Entry unload
        │
        ├── Remove the Config Entry event listener
        ├── Release registrations
        └── Remove only registrations with no remaining users
```

Config Entry reloads caused by Add or Edit rebuild the routing table from the
current persistent configuration.

---

# Future Synchronization Groups

Shared group-address registration does not itself synchronize independent
Scene Button Runtime instances.

Future synchronization groups will share logical Scene Mappings and Runtime
state while allowing each physical button binding to retain different group
addresses and local KNX scene numbers.

Synchronization will use logical scene identities rather than copying one
button's KNX scene number into another button.
