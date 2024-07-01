const puppeteer = require('puppeteer');

async function scrapeRates(url) {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: 'networkidle2' });

  // Adjust the selectors based on the website structure
  const rates = await page.evaluate(() => {
    const listings = document.querySelectorAll('.rate-listing'); // Adjust selector
    const results = [];

    listings.forEach(listing => {
      try {
        const provider = listing.querySelector('.provider-name').innerText.trim(); // Adjust selector
        const rateText = listing.querySelector('.rate').innerText.trim(); // Adjust selector
        const rate = parseFloat(rateText.replace('¢', '').replace('/kWh', '').trim()) / 100; // Convert to dollars

        results.push({ provider, rate });
      } catch (e) {
        // Handle errors if any elements are missing
        console.error('Error parsing listing:', e);
      }
    });

    return results;
  });

  await browser.close();
  return rates;
}

// Example usage
const url = 'https://www.choosetexaspower.org/';
scrapeRates(url).then(rates => {
  console.log('Available rates:', rates);

  // Replace this with the actual rate from your PDF
  const currentRate = 0.14100;

  const cheaperRates = rates.filter(rate => rate.rate < currentRate);
  if (cheaperRates.length > 0) {
    console.log('Cheaper rates found:');
    cheaperRates.forEach(rate => {
      console.log(`Provider: ${rate.provider}, Rate: $${rate.rate.toFixed(5)} per kWh`);
    });
  } else {
    console.log('No cheaper rates found.');
  }
}).catch(error => {
  console.error('Error:', error);
});
