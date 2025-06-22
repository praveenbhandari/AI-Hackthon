import { findFood } from './agents/foodfinder';

async function main() {
  try {
    // Test the food finder with a sample query
    console.log('Testing Food Finder...');
    const query = process.argv[2] || 'vegetarian Indian food';
    const location = process.argv[3] || 'San Francisco';
    
    console.log(`Searching for "${query}" in ${location}...`);
    
    const results = await findFood(query, location);
    
    console.log('Results:');
    console.log(JSON.stringify(results, null, 2));
  } catch (error) {
    console.error('Error in test script:', error);
  }
}

main();
