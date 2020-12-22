import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export const store = new Vuex.Store({
  state: {
    isConnected: false,
    socketMessage: '',
    tally: {
      tally0: 'none',
      tally1: 'none',
      tally2: 'none',
      tally3: 'none',
    },
    selected_tally: '',
    esp_dict: null,
  },
  mutations: {
    SET_TALLIES(state, value) {
      state.tally.tally0 = value[0];
      state.tally.tally1 = value[1];
      state.tally.tally2 = value[2];
      state.tally.tally3 = value[3];
    },
    SET_SELECTED_TALLY(state, value) {
      console.log(`Selected Tally: ${value}`);
      state.selected_tally = value;
    },
    SOCKET_CONNECT(state) {
      state.isConnected = true;
    },

    SOCKET_DISCONNECT(state) {
      state.isConnected = false;
    },
    SOCKET_MESSAGECHANNEL(state, message) {
      console.log(message);
      state.socketMessage = message;
    },
    SOCKET_update(state, value) {
      console.log(value);
      state.tally.tally0 = value[0];
      state.tally.tally1 = value[1];
      state.tally.tally2 = value[2];
      state.tally.tally3 = value[3];
    },
    SOCKET_espstate(state, value) {
      const list = [];
      // eslint-disable-next-line no-plusplus
      for (let i = 0; i < value.length; i++) {
        list.push(JSON.parse(value[i]));
      }
      state.esp_dict = list;
    },
  },
  getters: {
    getBG1: (state) => {
      const key = 'background-color:';
      switch (state.tally.tally0) {
        case 'l':
          return `${key} red`;
        case 'r':
          return `${key} green`;
        case 'n':
          return `${key} grey`;
        default:
          return `${key} amber`;
      }
    },
    getBG2: (state) => {
      const key = 'background-color:';
      switch (state.tally.tally1) {
        case 'l':
          return `${key} red`;
        case 'r':
          return `${key} green`;
        case 'n':
          return `${key} grey`;
        default:
          return `${key} amber`;
      }
    },
    getBG3: (state) => {
      const key = 'background-color:';
      switch (state.tally.tally2) {
        case 'l':
          return `${key} red`;
        case 'r':
          return `${key} green`;
        case 'n':
          return `${key} grey`;
        default:
          return `${key} amber`;
      }
    },
    getBG4: (state) => {
      const key = 'background-color:';
      switch (state.tally.tally3) {
        case 'l':
          return `${key} red`;
        case 'r':
          return `${key} green`;
        case 'n':
          return `${key} grey`;
        default:
          return `${key} amber`;
      }
    },
    getSelectedBackgroundColorTally: (state) => {
      const key = 'background-color:';
      switch (state.selected_tally.toString()) {
        case '0':
          switch (state.tally.tally0) {
            case 'l':
              return `${key} red`;
            case 'r':
              return `${key} green`;
            case 'n':
              return `${key} grey`;
            default:
              return `${key} amber`;
          }
        case '1':
          switch (state.tally.tally1) {
            case 'l':
              return `${key} red`;
            case 'r':
              return `${key} green`;
            case 'n':
              return `${key} grey`;
            default:
              return `${key} orange`;
          }
        case '2':
          switch (state.tally.tally2) {
            case 'l':
              return `${key} red`;
            case 'r':
              return `${key} green`;
            case 'n':
              return `${key} grey`;
            default:
              return `${key} orange`;
          }
        case '3':
          switch (state.tally.tally3) {
            case 'l':
              return `${key} red`;
            case 'r':
              return `${key} green`;
            case 'n':
              return `${key} grey`;
            default:
              return `${key} orange`;
          }
        default:
          return `${key} orange`;
      }
    },
  },
});
