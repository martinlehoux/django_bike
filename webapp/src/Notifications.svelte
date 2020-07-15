<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import moment from "moment";
  import { WebSocketMessage, WebSocketService, Notif } from "./service";

  let notifications: Array<Notif> = [];

  const service = new WebSocketService();
  let socket: WebSocket;

  onMount(async () => {
    service.socket.onmessage = function (event) {
      const data = JSON.parse(event.data);
      switch (data.type) {
        case "list":
          notifications = data.notifications.map((notif) => new Notif(notif));
          break;
        case "new":
          notifications = [new Notif(data.notification), ...notifications];
          break;
        case "delete":
          notifications = notifications.filter((notif) => notif.pk !== data.pk);
      }
    };
  });

  function deleteNotif(pk: number) {
    socket.send(JSON.stringify({ type: "delete", pk }));
  }
</script>

<main>
  {#each notifications as notification (notification.pk)}
    <div class="notification {notification.level} is-light">
      <button class="delete" on:click={() => deleteNotif(notification.pk)} />
      <p>{notification.content}</p>
      <p class="is-uppercase has-text-right has-text-weight-light is-size-7">
        {moment(notification.datetime).calendar()}
      </p>
    </div>
  {/each}
</main>
