<script lang="ts">
  import { onMount, onDestroy } from "svelte";

  let notifications = [];

  let notifGetter: number;

  onMount(async () => {
    // Fetch all
    fetch("/notification/")
      .then((res) => res.json())
      .then((data) => (notifications = data));
    notifGetter = setInterval(() => {
      fetch("/notification/")
        .then((res) => res.json())
        .then((data) => (notifications = data));
    }, 5000);
  });

  onDestroy(() => {
    clearInterval(notifGetter);
  });

  function deleteNotif(pk: number) {
    notifications = notifications.filter((notif) => notif.pk !== pk);
    fetch(`/notification/${pk}`, {
      method: "DELETE",
    });
  }
</script>

<main>
  {#each notifications as notification (notification.pk)}
    <div class="notification {notification.level}">
      <button class="delete" on:click={() => deleteNotif(notification.pk)} />
      {notification.content} ({notification.pk})
    </div>
  {/each}
</main>
