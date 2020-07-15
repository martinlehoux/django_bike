import Notification from './Notifications.svelte';

const app = new Notification({
	target: document.getElementById("svelte-root"),
});

export default app;
