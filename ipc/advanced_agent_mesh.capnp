@0xbf302d9a6c7188f1;

# ==============================================================================
# APEX TOWER OF BABEL: ADVANCED AGENT MESH IPC SCHEMA
# Standard: Zero-Copy Binary Serialization & Sub-Millisecond IPC Pass
# ==============================================================================

enum AgentRole {
  mastermind @0;
  reasoner @1;
  synthesizer @2;
  auditor @3;
  perception @4;
  operator @5;
  watchdog @6;
}

enum EpistemicTier {
  l0Presence @0;
  l1Structure @1;
  l2Behavior @2;
  l3ColossalBackend @3;
  l4TelemetrySelfHealing @4;
  l5SwarmEnterprise @5;
  l6SovereignAutonomy @6;
}

enum MessageType {
  taskMandate @0;
  intermediateProof @1;
  astBlock @2;
  auditFlag @3;
  synapticUpdate @4;
  heartbeat @5;
  emergencyHalt @6;
}

struct AgentIdentifier {
  agentId @0 :Text;
  role @1 :AgentRole;
  hostname @2 :Text;
  pid @3 :UInt32;
}

struct SynapticWeightUpdate {
  sourceEntity @0 :Text;
  targetEntity @1 :Text;
  deltaWeight @2 :Float32;
  currentWeight @3 :Float32;
  timestamp @4 :UInt64;
}

struct TelemetryMetric {
  metricName @0 :Text;
  metricValue @1 :Float64;
  unit @2 :Text;
}

struct AgentMessage {
  messageId @0 :Text;
  sequenceNumber @1 :UInt64;
  timestamp @2 :UInt64;
  msgType @3 :MessageType;
  sender @4 :AgentIdentifier;
  recipient @5 :AgentIdentifier;
  epistemicTier @6 :EpistemicTier;
  payloadUtf8 @7 :Text;
  payloadSha256 @8 :Text;
  synapticUpdates @9 :List(SynapticWeightUpdate);
  telemetryMetrics @10 :List(TelemetryMetric);
}

struct MeshRingBufferHeader {
  magicBytes @0 :UInt32;       # 0x41504558 (APEX)
  version @1 :UInt16;          # 1
  capacityBytes @2 :UInt32;
  writeOffset @3 :UInt32;
  readOffset @4 :UInt32;
  messageCount @5 :UInt64;
  lastHeartbeatEpoch @6 :UInt64;
}
