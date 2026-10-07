# 🛡️ SafeTox-AI

### AI-Based Toxic Gas Monitoring and Safe Entry Authorization System

SafeTox-AI is a smart safety monitoring system designed to protect **sewage and sanitation workers** from dangerous toxic gases before entering a sewage chamber.

The system monitors gas levels, classifies the risk level, verifies Personal Protective Equipment (PPE), and provides an entry authorization decision.

---

## 🚨 Problem Statement

Sewage workers may be exposed to dangerous gases such as:

* Hydrogen Sulfide (H₂S)
* Methane (CH₄)
* Ammonia (NH₃)
* Carbon Monoxide (CO)

Exposure to these gases can cause serious health problems and can become life-threatening in confined sewage environments.

Traditional safety checks may not continuously monitor the environment before entry.

**SafeTox-AI** provides a digital safety console that can be connected to gas sensors and safety hardware to support safer entry decisions.

---

## 💡 Proposed Solution

The system follows a simple safety workflow:

```text
Gas Sensors
     ↓
Gas Level Monitoring
     ↓
Risk Classification
     ↓
PPE Verification
     ↓
Supervisor Approval
     ↓
Entry Authorization
```

Entry is granted only when:

1. Gas conditions are safe.
2. Required PPE is verified.
3. Supervisor approval is provided.

---

## ✨ Features

* 🌫️ Toxic gas monitoring
* ⚠️ LOW / MEDIUM / HIGH risk classification
* 🟢🟡🔴 Visual risk indicators
* 🔔 Buzzer alert simulation
* 🦺 PPE verification
* 👷 Supervisor approval
* 🚪 Entry authorization
* 📋 Real-time event log
* 🌡️ Temperature and humidity display
* 🎛️ Normal, Moderate Gas Rise, and H₂S Leak simulation presets
* 🔄 Console reset functionality
* 🖥️ Interactive Streamlit dashboard

---

## 🧪 Monitored Gases

| Gas              | Formula | Unit | Sensor |
| ---------------- | ------- | ---- | ------ |
| Hydrogen Sulfide | H₂S     | ppm  | MQ-136 |
| Methane          | CH₄     | %LEL | MQ-2   |
| Ammonia          | NH₃     | ppm  | MQ-137 |
| Carbon Monoxide  | CO      | ppm  | MQ-7   |

---

## 📊 Risk Classification

The current demonstration version uses predefined safety thresholds.

| Risk | Descrip
