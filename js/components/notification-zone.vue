<template>
<div v-show="$root.notifications && $root.notifications.length > 0" class="notification-zone">
    <alert v-for="n in $root.notifications" :alert="n"></alert>
</div>
</template>

<script>
import Alert from 'components/alert.vue';
export default {
    name: 'notification-zone',
    components: {Alert}
};
</script>

<style lang="less">
.notification-zone {
    padding: 15px 15px 0;
    position: fixed;
    right: 0;
    bottom: 15px;
    max-width: 350px;
    z-index: 1001;

    .alert {
        &:last-child {
            margin-bottom: 0;
        }

        &:not(:last-child) {
            margin-bottom: 5px;
        }
    }
}
</style>
