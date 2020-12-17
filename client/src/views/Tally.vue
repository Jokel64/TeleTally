<template>
  <div :style="this.$store.getters.getSelectedBackgroundColorTally" class="fullscreen">
    <span>{{ this.$route.params.id }}</span>
  </div>
</template>

<script>
export default {
  name: 'Tally',
  data() {
    return {
      state: '',
      tally_id: '',
    };
  },
  computed: {

  },
  methods: {
  },
  created() {
    this.tally_id = this.$route.params.id;
    this.$store.commit('SET_SELECTED_TALLY', Number(this.$route.params.id) - 1);
  },
  updated() {
    this.tally_id = this.$route.params.id;
    this.$store.commit('SET_SELECTED_TALLY', Number(this.$route.params.id) - 1);
  },
};
</script>

<style scoped>
span {
  font-size: 40vmin;
  height: 100%;
  font-weight: bolder;
}

.fullscreen {
  height: 100%;
}
</style>
