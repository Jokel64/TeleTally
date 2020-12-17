<template>
  <div id="app" style="height: 100%">
    <div v-bind:style="bgcolor" class="fullscreen">
      <div id="nav">
        <router-link to="/">Home</router-link>

        |
        <router-link v-for="tally in tallies" :key="tally.val"
                     :to="{path: '/tally/' + tally.label, params: {tally_id:tally.val } }"> |
          Tally {{
            tally.label
          }}
        </router-link>
        |
        <router-link to="/settings">Settings</router-link>

      </div>
      <router-view/>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Ping',
  data() {
    return {
      msg: '',

      tallies: this.generateTallies(),
    };
  },
  computed: {
    bgcolor() {
      console.log('UPDATE!!!!');
      switch (this.$store.state.selected_tally) {
        case '0':
          return this.$store.getters.getBackgroundColorTally0;
        case '1':
          return this.$store.getters.getBackgroundColorTally1;
        case '2':
          return this.$store.getters.getBackgroundColorTally2;
        case '3':
          return this.$store.getters.getBackgroundColorTally3;
        default:
          return 'background-color: amber';
      }
    },
  },
  methods: {
    generateTallies() {
      const returnValue = new Array(4);
      for (let i = 0; i < 4; i += 1) {
        returnValue[i] = {
          val: i,
          label: i + 1,
        };
      }
      return returnValue;
    },
  },
  created() {
    this.$store.dispatch('getStateFromServer');
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}

html, body {
  height: 100%;
}

.fullscreen{
  height: 100%;
}
</style>
