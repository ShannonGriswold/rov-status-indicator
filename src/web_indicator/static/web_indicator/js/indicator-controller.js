/**
 * LAMPI Web Controller (Django Version)
 *
 * This module implements the Alpine.js component that controls the LAMPI
 * smart lamp through MQTT over WebSockets.
 *
 * Configuration is passed from Django via window.LAMPI_CONFIG
 */

import mqtt from 'mqtt';

// ============================================================================
// Configuration Constants (from Django)
// ============================================================================

// Get configuration from Django template
// Django provides: deviceId, mqtt settings, and complete MQTT topic strings
const CONFIG = window.INDICATOR_CONFIG || {};
const HOST_ADDRESS = CONFIG.mqtt?.hostname || window.location.hostname;
const HOST_PORT = CONFIG.mqtt?.websocketsPort || 50002;

// Generate a unique client ID to identify this browser session
const CLIENT_ID = Math.random().toString(36).substring(2) + '_web_client';

// MQTT topics are provided by Django - no client-side topic synthesis needed
// CONFIG.topics contains: setConfig, lampChanged, lampServiceState, lampUIState

// ============================================================================
// Alpine.js Component Definition
// ============================================================================

/**
 * Creates the lamp controller Alpine.js component
 */
function indicatorController() {
  return {
    // ========================================================================
    // Reactive State Properties
    // ========================================================================

    // Lamp state (0.0 to 1.0 for sliders, boolean for power)
    armed: false,
    pi_connected: false,
    ardusub_connected: false,
    flooding: false,

    // Internal state
    client: null,
    updateTimer: null,
    hasReceivedInitialState: false,

    // ========================================================================
    // Computed Properties (Getters)
    // ========================================================================
    armed_text() {
        let text = this.armed ? "Armed" : "Disarmed";
        return text;
    },

    pi_text() {
        let text = this.pi_connected ? "Pi Connected" : "Pi Disconnected";
        return text;
    },

    ardusub_text() {
        let text = this.ardusub_connected ? "Ardusub Connected" : "Ardusub Disconnected";
        return text;
    },

    flooding_text() {
        let text = this.flooding ? "Water detected" : "No water detected";
        return text;
    },

    indicator_color(indicator_value) {
        return indicator_value ? 'lime' : 'red';
    },

    // ========================================================================
    // MQTT Connection Methods
    // ========================================================================

    connect() {
      const brokerUrl = `ws://${HOST_ADDRESS}:${HOST_PORT}/`;

      this.client = mqtt.connect(brokerUrl, {
        clientId: CLIENT_ID,
        clean: true,
        reconnectPeriod: 1000,
        forceNativeWebSocket: true
      });

      this.client.on('connect', () => {
        console.log('Connected to MQTT broker');
        this.mqttConnected = true;

        this.client.subscribe(CONFIG.topics.vehicleState, (err) => {
          if (err) {
            console.error('Failed to subscribe to vehicle state:', err);
          }
        });

        this.client.subscribe(CONFIG.topics.flooding, (err) => {
          if (err) {
            console.error('Failed to subscribe to flooding:', err);
          }
        });
      });

      this.client.on('message', (topic, payload) => {
        this.onMessageArrived(topic, payload.toString());
      });

      this.client.on('close', () => {
        console.log('Disconnected from MQTT broker');
        this.mqttConnected = false;
        this.deviceConnected = false;
      });

      this.client.on('error', (err) => {
        console.error('MQTT error:', err);
      });
    },

    // ========================================================================
    // MQTT Message Handlers
    // ========================================================================

    onMessageArrived(topic, payloadString) {

      // Parse JSON for other messages
      let payload;
      try {
        payload = JSON.parse(payloadString);
      } catch (e) {
        console.error('Failed to parse MQTT message:', e);
        return;
      }

      console.log("recieved a message");

      if (topic === CONFIG.topics.vehicleState) {
        console.log("recieved vehicleState");
        this.onVehicleStateMessage(payload);
      }

      if (topic === CONFIG.topics.flooding) {
        this.onFloodingMessage(payload);
      }
    },

    onVehicleStateMessage(payload) {
      this.armed = payload.armed;
      this.pi_connected = payload.pi_connected;
      this.ardusub_connected = payload.ardusub_connected;
      this.hasReceivedInitialState = true;
    },

    onFloodingMessage(payload) {
      this.flooding = payload.flooding;
    },

    // ========================================================================
    // UI Event Handlers
    // ========================================================================

    // ========================================================================
    // MQTT Publishing Methods
    // ========================================================================
    sendArm(status) {
      if (!this.client || !this.mqttConnected) {
        return;
      }
      let arm = {
        armed: status,
      }

      this.client.publish(CONFIG.topics.arm, JSON.stringify(arm));
    }
  };
}

// Make the component available to Alpine.js
window.indicatorController = indicatorController;
