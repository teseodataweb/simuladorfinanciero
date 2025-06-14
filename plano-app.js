import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

console.log("✅ plano-app.js con enfoque 3D restaurado");

// ESCENA
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf0f0f0);

// CÁMARA PERSPECTIVA
const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 1, 1000);
camera.position.set(0, 16, 16); // o incluso (0, 12, 12)
camera.lookAt(0, 0, 0);

// RENDER
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// LUCES
scene.add(new THREE.AmbientLight(0xffffff, 0.6));
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(20, 50, 20);
scene.add(light);

// CONTROLES
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.minPolarAngle = Math.PI / 3; // evita mirar desde abajo
controls.maxPolarAngle = Math.PI / 2; // tope cenital
controls.enablePan = false;
controls.minDistance = 30;
controls.maxDistance = 90;

// COLORES
const colores = {
  disponible: 0xffff00,
  vendido: 0xd39d53,
  amenidad: 0x2ecc71,
  'no-disponible': 0x7f8c8d
};

// TOOLTIP
const tooltip = document.createElement('div');
tooltip.style.position = 'absolute';
tooltip.style.background = '#fff';
tooltip.style.border = '1px solid #ccc';
tooltip.style.padding = '6px 10px';
tooltip.style.borderRadius = '6px';
tooltip.style.boxShadow = '0 2px 6px rgba(0,0,0,0.2)';
tooltip.style.fontFamily = 'Arial';
tooltip.style.fontSize = '13px';
tooltip.style.display = 'none';
tooltip.style.pointerEvents = 'none';
document.body.appendChild(tooltip);

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

// PARÁMETROS
const totalCols = 10;
const spacing = 5;

// CARGAR LOTES
fetch('lotes.json')
  .then(res => res.json())
  .then(data => {
    const lotes = data.lotes;
    const textureLoader = new THREE.TextureLoader();
    const calleTexture = textureLoader.load('asfalto.png'); // usa tu textura local
    
    lotes.forEach((lote, i) => {
      const estado = lote.estado;
      const geometry = new THREE.BoxGeometry(3.5, 1.2, 3.5); // lote largo y bajo

      const material = new THREE.MeshStandardMaterial({
                color: colores[estado] || 0xcccccc });
      const cube = new THREE.Mesh(geometry, material);
      cube.userData = lote;

      const col = i % totalCols;
      const row = Math.floor(i / totalCols);
      const posX = (col - totalCols / 2) * spacing + spacing / 2;
      const posY = 0.6;
      const posZ = row === 0 ? -4 : 4;

      cube.position.set(posX, posY, posZ);
      scene.add(cube);

      // Cercas rectas (edges)
      const edgeGeo = new THREE.EdgesGeometry(geometry);
      const edges = new THREE.LineSegments(edgeGeo, new THREE.LineBasicMaterial({ color: 0x000000 }));
      edges.position.copy(cube.position);
      scene.add(edges);
    });

    // Calle central
    const calle = new THREE.Mesh(
      new THREE.PlaneGeometry(totalCols * spacing, 8),
      new THREE.MeshStandardMaterial({ color: 0xe0e0e0, side: THREE.DoubleSide })
    );
    calle.rotation.x = -Math.PI / 2;
    calle.position.y = 0.01;
    scene.add(calle);
  })
  .catch(err => console.error('❌ Error al cargar lotes:', err));
  controls.target.set(0, 0, 0);
  controls.update();
  
// MOUSE HOVER INFO
window.addEventListener('mousemove', (event) => {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(scene.children);

  const intersected = intersects.find(obj => obj.object.userData?.id);
  if (intersected) {
    const { id, estado, medida = 'Sin medida' } = intersected.object.userData;
    tooltip.innerHTML = `<strong>${id}</strong><br>${estado}<br>${medida}`;
    tooltip.style.left = event.clientX + 10 + 'px';
    tooltip.style.top = event.clientY + 10 + 'px';
    tooltip.style.display = 'block';
  } else {
    tooltip.style.display = 'none';
  }
});

// RENDER LOOP
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
