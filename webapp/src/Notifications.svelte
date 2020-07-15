<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { HttpService, Notif } from "./service";

  let notifications = [];
  let notifGetter: number;

  const httpService = new HttpService();

  onMount(async () => {
    // Fetch all
    httpService.getNotifications().then((data) => (notifications = data));
    notifGetter = setInterval(() => {
      httpService.getNotifications().then((data) => (notifications = data));
    }, 5000);
  });

  onDestroy(() => {
    clearInterval(notifGetter);
  });

  function deleteNotif(pk: number) {
    notifications = notifications.filter((notif) => notif.pk !== pk);
    httpService.deleteNotification(pk);
  }
</script>

<main>
  {#each notifications as notification (notification.pk)}
    <div class="notification {notification.level} is-light">
      <button class="delete" on:click={() => deleteNotif(notification.pk)} />
      {notification.content}
    </div>
  {/each}
</main>
