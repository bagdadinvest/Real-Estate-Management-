// ESM module to initialize a reusable rotating Earth globe
// Usage from a Django template (example):
// import { initEarthGlobe } from "<static>/newfront/assets/js/earth-globe-init.js";
// initEarthGlobe('#globe', { threeUrl: '<static>/build/three.module.min.js', orbitUrl: '<static>/jsm/controls/OrbitControls.js', texturesBaseUrl: '<static>/textures/planets/', lat: 41.0082, lon: 28.9784, autoRotateSpeed: 0.025, showStars: true, popupSelector: '#popup' });

export async function initEarthGlobe(target, options = {}) {
  const el = typeof target === 'string' ? document.querySelector(target) : target;
  if (!el) return;

  const threeUrl = options.threeUrl;
  const orbitUrl = options.orbitUrl;
  if (!threeUrl || !orbitUrl) {
    throw new Error('initEarthGlobe requires threeUrl and orbitUrl');
  }

  const THREE = await import(threeUrl);
  const OrbitControlsModule = await import(orbitUrl);
  const OrbitControls = OrbitControlsModule.OrbitControls || OrbitControlsModule.default || OrbitControlsModule;

  const texturesBaseUrl = options.texturesBaseUrl || '/static/textures/planets/';
  const lat = typeof options.lat === 'number' ? options.lat : null;
  const lon = typeof options.lon === 'number' ? options.lon : null;
  const autoRotateSpeed = typeof options.autoRotateSpeed === 'number' ? options.autoRotateSpeed : 0.025;
  const showStars = options.showStars !== false; // default true
  const cloudsOpacity = typeof options.cloudsOpacity === 'number' ? options.cloudsOpacity : 0.7;
  const popupSelector = options.popupSelector || null;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(25, 1, 0.1, 100);
  camera.position.set(4.5, 2, 3);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  el.appendChild(renderer.domElement);

  // Lights
  const ambient = new THREE.AmbientLight(0xffffff, 0.45);
  scene.add(ambient);
  const sun = new THREE.DirectionalLight('#ffffff', 1.25);
  sun.position.set(0, 0, 3);
  scene.add(sun);

  // Textures & materials
  const loader = new THREE.TextureLoader();
  const dayTexture = loader.load(texturesBaseUrl + 'earth_day_4096.jpg');
  dayTexture.colorSpace = THREE.SRGBColorSpace;
  dayTexture.anisotropy = 8;
  const normalTexture = loader.load(texturesBaseUrl + 'earth_normal_2048.jpg');
  const specularTexture = loader.load(texturesBaseUrl + 'earth_specular_2048.jpg');
  const cloudsTexture = loader.load(texturesBaseUrl + 'earth_clouds_2048.png');

  const globeGeom = new THREE.SphereGeometry(1, 64, 64);
  const globeMat = new THREE.MeshPhongMaterial({
    map: dayTexture,
    specularMap: specularTexture,
    bumpMap: normalTexture,
    bumpScale: 0.15,
    shininess: 15,
    specular: new THREE.Color(0x333333)
  });
  const globe = new THREE.Mesh(globeGeom, globeMat);
  scene.add(globe);

  // Clouds
  const clouds = new THREE.Mesh(
    new THREE.SphereGeometry(1.01, 64, 64),
    new THREE.MeshLambertMaterial({ map: cloudsTexture, transparent: true, opacity: cloudsOpacity, depthWrite: false })
  );
  scene.add(clouds);

  // Stars
  let stars = null;
  if (showStars) {
    const starGeom = new THREE.BufferGeometry();
    const starCount = 600;
    const positions = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount; i++) {
      const r = 25 * Math.cbrt(Math.random());
      const theta = Math.random() * 2 * Math.PI;
      const phi = Math.acos(2 * Math.random() - 1);
      positions[i * 3 + 0] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = r * Math.cos(phi);
    }
    starGeom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    stars = new THREE.Points(starGeom, new THREE.PointsMaterial({ color: 0xffffff, size: 0.02 }));
    scene.add(stars);
  }

  // Controls
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.minDistance = 0.8;
  controls.maxDistance = 50;

  // Marker
  let marker = null;
  if (lat !== null && lon !== null) {
    marker = new THREE.Mesh(
      new THREE.SphereGeometry(0.02, 16, 16),
      new THREE.MeshBasicMaterial({ color: '#ff0000' })
    );
    marker.position.copy(latLonToVector3(lat, lon, 1.02));
    globe.add(marker);
  }

  // Resize
  function resize() {
    const rect = el.getBoundingClientRect();
    const width = Math.max(1, rect.width);
    const height = Math.max(1, rect.height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  }
  new ResizeObserver(resize).observe(el);
  window.addEventListener('orientationchange', resize);
  resize();

  const clock = new THREE.Clock();
  function animate() {
    const delta = clock.getDelta();
    globe.rotation.y += delta * autoRotateSpeed;
    clouds.rotation.y += delta * (autoRotateSpeed + 0.005);
    if (stars) stars.rotation.y += delta * 0.0008;

    controls.update();

    if (marker && popupSelector) {
      const worldPos = marker.getWorldPosition(new THREE.Vector3());
      const vector = worldPos.clone().project(camera);
      const popup = document.querySelector(popupSelector);
      if (popup) {
        const rect = el.getBoundingClientRect();
        const x = rect.left + (vector.x * 0.5 + 0.5) * rect.width;
        const y = rect.top + (vector.y * -0.5 + 0.5) * rect.height;
        popup.style.transform = `translate(-50%, -50%) translate(${x}px,${y - 20}px)`;
        popup.style.display = 'block';
      }
    }

    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  }
  requestAnimationFrame(animate);
}

function latLonToVector3(latitude, longitude, radius) {
  const phi = (90 - latitude) * (Math.PI / 180);
  const theta = (longitude + 180) * (Math.PI / 180);
  const x = -(radius * Math.sin(phi) * Math.cos(theta));
  const y = radius * Math.cos(phi);
  const z = radius * Math.sin(phi) * Math.sin(theta);
  return new (window.THREE?.Vector3 || (class V3 { constructor(x,y,z){ this.x=x; this.y=y; this.z=z; } })) (x, y, z);
}

