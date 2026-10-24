// Retire the previous Flutter worker and its caches during the static-site move.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    await Promise.all(['flutter-app-cache', 'flutter-temp-cache', 'flutter-app-manifest']
      .map(name => caches.delete(name)));
    await self.clients.claim();
    const windows = await self.clients.matchAll({type: 'window'});
    await self.registration.unregister();
    await Promise.all(windows.map(client => client.navigate(client.url)));
  })());
});
