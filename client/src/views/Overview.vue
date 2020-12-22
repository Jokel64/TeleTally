<template>
  <div class="home">
    <table>

      <tr>
        <td rowspan="2" v-bind:style="this.$store.getters.getBG2">LINKS</td>
        <td
          v-bind:style="this.$store.getters.getBG3">DOM
        </td>
        <td rowspan="2" v-bind:style="this.$store.getters.getBG1">RECHTS</td>
      </tr>
      <tr>
        <td v-bind:style="this.$store.getters.getBG4">MOBIL</td>
      </tr>

    </table>
  </div>
</template>

<script>
// @ is an alias to /src

export default {
  name: 'Home',
  created() {
    this.$socket.emit('apirequest', 'update');
  },
};
</script>

<style scoped>
body {
  background-color: white;
}

.home {
  height: 100%;
  color: white;
  font-size: larger;
}

table {

  width: 100%;
  height: 100%;
}

td {

  width: 30%;
  text-align: center;
  font-size: 3em;
  font-family: sans-serif;
}

</style>
