<template>
  <div>  <h1>Settings</h1>
  <button v-on:click="sendMessage">Clikc Me</button></div>
</template>

<script>
export default {
  name: 'Settings',
  methods: {
    sendMessage() {
      console.log('Clicked!');
      this.$socket.emit('kanal', 'nachricht');
    },
  },
};
</script>

<style scoped>

</style>
