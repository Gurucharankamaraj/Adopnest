const pets = [
  { id: 'P001', name: 'Buddy', type: 'Dog', breed: 'Labrador', image: 'https://www.101dogbreeds.com/wp-content/uploads/2018/10/Labrador-Retriever-Puppies.jpg' },
  { id: 'P002', name: 'Charlie', type: 'Dog', breed: 'Beagle', image: 'https://www.zooplus.de/magazin/wp-content/uploads/2017/03/2-Jahre-Beagle.jpg' },
  { id: 'P003', name: 'Rocky', type: 'Dog', breed: 'Golden Retriever', image: 'https://i.shgcdn.com/148dc4ae-078b-4962-a7ba-70b75be8df4e/-/format/auto/-/preview/3000x3000/-/quality/lighter/' },
  { id: 'P004', name: 'Max', type: 'Dog', breed: 'German Shepherd', image: 'https://animalso.com/wp-content/uploads/2017/01/german-shepherd-puppies_3.jpg' },
  { id: 'P005', name: 'Cooper', type: 'Dog', breed: 'Poodle', image: 'https://www.coopsandcages.com.au/wp-content/uploads/2021/10/The-Poodle-Dog-Breed.png' },
  { id: 'P006', name: 'Duke', type: 'Dog', breed: 'Bulldog', image: 'https://www.thesprucepets.com/thmb/zXkzVVV5P8h2JG0ZUFtXtvIq-lM=/3600x0/filters:no_upscale():strip_icc()/bulldog-4584344-hero-8b60f1e867f046e792ba092eec669256.jpg' },
  { id: 'P007', name: 'Whiskers', type: 'Cat', breed: 'Siamese', image: 'https://www.litter-robot.com/media/blog/alex-meier-siamese.jpg' },
  { id: 'P008', name: 'Luna', type: 'Cat', breed: 'Persian', image: 'https://e0.pxfuel.com/wallpapers/476/194/desktop-wallpaper-my-amazing-persian-prince-persian-cat-white-cats-white-cats.jpg' },
  { id: 'P009', name: 'Milo', type: 'Cat', breed: 'Maine Coon', image: 'https://www.thesprucepets.com/thmb/MzKr6fC-v8W4D4oz2p9wWCwAFms=/2119x0/filters:no_upscale():strip_icc()/GettyImages-1189893683-e0ff70596b3b4f0687ba573e5a671f74.jpg' },
  { id: 'P010', name: 'Shadow', type: 'Cat', breed: 'British Shorthair', image: 'https://lunarosebritishshorthairs.co.uk/wp-content/uploads/2020/08/british_shorthair_kitten_lunarose_cats59.jpg' },
  { id: 'P011', name: 'Zoe', type: 'Cat', breed: 'Ragdoll', image: 'https://www.floppycats.com/wp-content/uploads/2020/04/Seal-Mitted-Ragdoll-Cat-Charlie-with-an-hourglass-blaze-outside-on-grass-IMG_1730-scaled.jpg' },
  { id: 'P012', name: 'Cleo', type: 'Cat', breed: 'Bengal', image: 'https://i0.wp.com/petradioshow.com/wp-content/uploads/2014/08/306059656_c4fafc4a87_o.jpg' }
];

const petList = document.getElementById('pet-list');
const filter = document.getElementById('filter');

function displayPets(type) {
  petList.innerHTML = '';
  pets.filter(p => type === 'all' || p.type === type).forEach(pet => {
    const div = document.createElement('div');
    div.classList.add('pet-card');
    div.innerHTML = `
      <img src="${pet.image}" alt="${pet.name}"/>
      <h4>${pet.name}</h4>
      <p><strong>Breed:</strong> ${pet.breed}</p>
      <p><strong>Type:</strong> ${pet.type}</p>
      <p><strong>ID:</strong> ${pet.id}</p>
    `;
    petList.appendChild(div);
  });
}

filter.addEventListener('change', e => displayPets(e.target.value));

window.onload = () => displayPets('all');
