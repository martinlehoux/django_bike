import Notification from './Notifications.svelte';

const notification = new Notification({
	target: document.getElementById("svelte-root"),
});

export default {
	notification,
};
