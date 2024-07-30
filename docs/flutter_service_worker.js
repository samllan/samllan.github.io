'use strict';
const MANIFEST = 'flutter-app-manifest';
const TEMP = 'flutter-temp-cache';
const CACHE_NAME = 'flutter-app-cache';

const RESOURCES = {"assets/NOTICES": "3cefb71748d3bc92ca2cdbd0b06504bf",
"assets/AssetManifest.bin.json": "dac862512a939ccc543846e5b68fbd3e",
"assets/FontManifest.json": "dc3d03800ccca4601324923c0b1d6d57",
"assets/assets/project12-pexels-thatguycraig000-1563355.jpg": "39065f1a5d0cf52d568f66cbc1e5204a",
"assets/assets/ice_segmentation.png": "d7e6774b6a0c1c69c7fc3d71aba8baf9",
"assets/assets/kaggle_health_hackathon.webp": "bbc78356ba800b2819059050d8e1eba4",
"assets/assets/project6-pexels-eberhardgross-1624496.jpg": "f56c25141ba9d5d90451e3a9f9aaf611",
"assets/assets/events_old.webp": "2b2c81e07ff656bc9bbd336d42f5f9eb",
"assets/assets/train_game.webp": "395ebf5c1f7613dd44873e901788f7f8",
"assets/assets/project11-pexels-sohi-807598.jpg": "b501a86f7e9f1a1e6fa856ce9ac1aa9d",
"assets/assets/gen_ai_med_teacher_pexels-cottonbro-7579829.jpg": "42ad321e21b25f3d137c227d01757749",
"assets/assets/things_i_learnt_pexels-singkham-178541-1108572.jpg": "98f1ab8ed86474a3e6749f6fbba6c4d5",
"assets/assets/project4-pexels-eberhardgross-443446.jpg": "465bbb69b27d8023a8f348552b7b2b21",
"assets/assets/project3-pexels-eberhardgross-443446.jpg": "de2dc494344a3ee0052f1e6168bb2f4b",
"assets/assets/strathclyde%2520boat%2520bulding.jpg": "4c1aabe78cd828c77d0b5004be562596",
"assets/assets/ai2%2520logo.png": "8cc80fb1b414ba62f11a31c1c8e54317",
"assets/assets/project2-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg": "c55a779bc0fde4a7d9b2dbaab9f76bb5",
"assets/assets/project9-pexels-pixabay-60597.jpg": "839eb3afe6317cbcc9a57ef04b75d42b",
"assets/assets/ST_A_bacteria_fluorescent.jpg": "889e6641240f4dfbd3eb1285361a63db",
"assets/assets/weather%2520fourier%2520series%2520modelling.webp": "a76a6ff7603ab5ad4b6b7ca9bbfcf718",
"assets/assets/trad_ML.webp": "3d211217953f65d1baae5e5e36689235",
"assets/assets/heart%2520question%2520mark.webp": "fdb19772c89a025a9e0b272623c5a2ca",
"assets/assets/reinforcement_learning.webp": "026300fc5b7b25eb1e01a16fc606cf30",
"assets/assets/project1-nice-clear-light-bulbs-eujn90ms9da1bw9j.jpg": "1d9348aafc24cab7109d9ad3d688bb40",
"assets/assets/project10-pexels-pixabay-326055.jpg": "9981cade61ce5540dab66c8a9c47cd69",
"assets/assets/kaggle_nature_hackathon.webp": "7121ce7fce9bb0bfd745abba9025e5f2",
"assets/assets/events.webp": "277254b76c3f1327064afbd32fbc00c1",
"assets/assets/project7-pexels-pixabay-33045.jpg": "ece4b7622fdd9022ebba91c3ff8e932b",
"assets/assets/words_full_stack.png": "09f2c7d5b2714e5ec5b76b87e3c47097",
"assets/assets/project8-pexels-pixabay-33109.jpg": "4f3ce7c8645c6e55455b2a136ca8f048",
"assets/assets/lane_detection.jpg": "0f1f12ca45fe6c742a3851037c9780d8",
"assets/assets/vision_transformer.webp": "8b0ab8379fb2cc63c10e3c1c726073d6",
"assets/assets/strathclyde%2520boat%2520bulding%2520old.jpg": "6a5c34680d30498e965b7d52593e04c2",
"assets/assets/project13-pexels-vladalex94-1402787.jpg": "519e6031276f53f8bc0647e1c7030112",
"assets/assets/project5-pexels-eberhardgross-1366919.jpg": "b520a341d3383ffe9360b3d5da50479b",
"assets/assets/explainable_AI.webp": "5951c8401519e36df2d9867e2ffcb2f7",
"assets/assets/DRT_pexels-philippedonn-1169754.jpg": "d9abeb21b9e4701c19a0f141eb6d10af",
"assets/fonts/MaterialIcons-Regular.otf": "0db35ae7a415370b89e807027510caf0",
"assets/AssetManifest.json": "4e0acb4e00281824a63de3adbbcb3cac",
"assets/AssetManifest.bin": "5133c599cc2ff1ae1e8007cd661beae2",
"assets/shaders/ink_sparkle.frag": "ecc85a2e95f5e9f53123dcaf8cb9b6ce",
"assets/packages/cupertino_icons/assets/CupertinoIcons.ttf": "e986ebe42ef785b27164c36a9abc7818",
"index.html": "ef3f12c6930024ea0768107d01a2c197",
"/": "ef3f12c6930024ea0768107d01a2c197",
"flutter.js": "383e55f7f3cce5be08fcf1f3881f585c",
"canvaskit/canvaskit.wasm": "9251bb81ae8464c4df3b072f84aa969b",
"canvaskit/skwasm.worker.js": "bfb704a6c714a75da9ef320991e88b03",
"canvaskit/canvaskit.js": "738255d00768497e86aa4ca510cce1e1",
"canvaskit/canvaskit.js.symbols": "74a84c23f5ada42fe063514c587968c6",
"canvaskit/skwasm.wasm": "4051bfc27ba29bf420d17aa0c3a98bce",
"canvaskit/skwasm.js.symbols": "c3c05bd50bdf59da8626bbe446ce65a3",
"canvaskit/skwasm.js": "5d4f9263ec93efeb022bb14a3881d240",
"canvaskit/chromium/canvaskit.wasm": "399e2344480862e2dfa26f12fa5891d7",
"canvaskit/chromium/canvaskit.js": "901bb9e28fac643b7da75ecfd3339f3f",
"canvaskit/chromium/canvaskit.js.symbols": "ee7e331f7f5bbf5ec937737542112372",
"flutter_bootstrap.js": "518d90d291a5044fcf0b54f2edb7dd8b",
"main.dart.js": "f167471b8ebdae4d2deb5f8197c1c7fe",
"icons/Icon-maskable-512.png": "301a7604d45b3e739efc881eb04896ea",
"icons/Icon-maskable-192.png": "c457ef57daa1d16f64b27b786ec2ea3c",
"icons/Icon-512.png": "96e752610906ba2a93c65f8abe1645f1",
"icons/Icon-192.png": "ac9a721a12bbc803b44f645561ecb1e1",
"manifest.json": "39d73f4d1aa293411e41045f4a83569a",
"version.json": "c8f0614c28e849d51f70336945a526a9",
"favicon.png": "5dcef449791fa27946b3d35ad8803796"};
// The application shell files that are downloaded before a service worker can
// start.
const CORE = ["main.dart.js",
"index.html",
"flutter_bootstrap.js",
"assets/AssetManifest.bin.json",
"assets/FontManifest.json"];

// During install, the TEMP cache is populated with the application shell files.
self.addEventListener("install", (event) => {
  self.skipWaiting();
  return event.waitUntil(
    caches.open(TEMP).then((cache) => {
      return cache.addAll(
        CORE.map((value) => new Request(value, {'cache': 'reload'})));
    })
  );
});
// During activate, the cache is populated with the temp files downloaded in
// install. If this service worker is upgrading from one with a saved
// MANIFEST, then use this to retain unchanged resource files.
self.addEventListener("activate", function(event) {
  return event.waitUntil(async function() {
    try {
      var contentCache = await caches.open(CACHE_NAME);
      var tempCache = await caches.open(TEMP);
      var manifestCache = await caches.open(MANIFEST);
      var manifest = await manifestCache.match('manifest');
      // When there is no prior manifest, clear the entire cache.
      if (!manifest) {
        await caches.delete(CACHE_NAME);
        contentCache = await caches.open(CACHE_NAME);
        for (var request of await tempCache.keys()) {
          var response = await tempCache.match(request);
          await contentCache.put(request, response);
        }
        await caches.delete(TEMP);
        // Save the manifest to make future upgrades efficient.
        await manifestCache.put('manifest', new Response(JSON.stringify(RESOURCES)));
        // Claim client to enable caching on first launch
        self.clients.claim();
        return;
      }
      var oldManifest = await manifest.json();
      var origin = self.location.origin;
      for (var request of await contentCache.keys()) {
        var key = request.url.substring(origin.length + 1);
        if (key == "") {
          key = "/";
        }
        // If a resource from the old manifest is not in the new cache, or if
        // the MD5 sum has changed, delete it. Otherwise the resource is left
        // in the cache and can be reused by the new service worker.
        if (!RESOURCES[key] || RESOURCES[key] != oldManifest[key]) {
          await contentCache.delete(request);
        }
      }
      // Populate the cache with the app shell TEMP files, potentially overwriting
      // cache files preserved above.
      for (var request of await tempCache.keys()) {
        var response = await tempCache.match(request);
        await contentCache.put(request, response);
      }
      await caches.delete(TEMP);
      // Save the manifest to make future upgrades efficient.
      await manifestCache.put('manifest', new Response(JSON.stringify(RESOURCES)));
      // Claim client to enable caching on first launch
      self.clients.claim();
      return;
    } catch (err) {
      // On an unhandled exception the state of the cache cannot be guaranteed.
      console.error('Failed to upgrade service worker: ' + err);
      await caches.delete(CACHE_NAME);
      await caches.delete(TEMP);
      await caches.delete(MANIFEST);
    }
  }());
});
// The fetch handler redirects requests for RESOURCE files to the service
// worker cache.
self.addEventListener("fetch", (event) => {
  if (event.request.method !== 'GET') {
    return;
  }
  var origin = self.location.origin;
  var key = event.request.url.substring(origin.length + 1);
  // Redirect URLs to the index.html
  if (key.indexOf('?v=') != -1) {
    key = key.split('?v=')[0];
  }
  if (event.request.url == origin || event.request.url.startsWith(origin + '/#') || key == '') {
    key = '/';
  }
  // If the URL is not the RESOURCE list then return to signal that the
  // browser should take over.
  if (!RESOURCES[key]) {
    return;
  }
  // If the URL is the index.html, perform an online-first request.
  if (key == '/') {
    return onlineFirst(event);
  }
  event.respondWith(caches.open(CACHE_NAME)
    .then((cache) =>  {
      return cache.match(event.request).then((response) => {
        // Either respond with the cached resource, or perform a fetch and
        // lazily populate the cache only if the resource was successfully fetched.
        return response || fetch(event.request).then((response) => {
          if (response && Boolean(response.ok)) {
            cache.put(event.request, response.clone());
          }
          return response;
        });
      })
    })
  );
});
self.addEventListener('message', (event) => {
  // SkipWaiting can be used to immediately activate a waiting service worker.
  // This will also require a page refresh triggered by the main worker.
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
    return;
  }
  if (event.data === 'downloadOffline') {
    downloadOffline();
    return;
  }
});
// Download offline will check the RESOURCES for all files not in the cache
// and populate them.
async function downloadOffline() {
  var resources = [];
  var contentCache = await caches.open(CACHE_NAME);
  var currentContent = {};
  for (var request of await contentCache.keys()) {
    var key = request.url.substring(origin.length + 1);
    if (key == "") {
      key = "/";
    }
    currentContent[key] = true;
  }
  for (var resourceKey of Object.keys(RESOURCES)) {
    if (!currentContent[resourceKey]) {
      resources.push(resourceKey);
    }
  }
  return contentCache.addAll(resources);
}
// Attempt to download the resource online before falling back to
// the offline cache.
function onlineFirst(event) {
  return event.respondWith(
    fetch(event.request).then((response) => {
      return caches.open(CACHE_NAME).then((cache) => {
        cache.put(event.request, response.clone());
        return response;
      });
    }).catch((error) => {
      return caches.open(CACHE_NAME).then((cache) => {
        return cache.match(event.request).then((response) => {
          if (response != null) {
            return response;
          }
          throw error;
        });
      });
    })
  );
}
