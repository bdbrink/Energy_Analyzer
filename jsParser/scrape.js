const puppeteer = require('puppeteer');

async function scrapeRates(url) {
  const browser = await puppeteer.launch({ headless: false }); // Set to false for debugging
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: 'networkidle2' });

  console.log(`Navigated to ${url}`);

  // Wait for the rate cards to load
  await page.waitForSelector('.rate-card', { timeout: 10000 });

  const rates = await page.evaluate(() => {
    const results = [];
    const offers = document.querySelectorAll('.rate-card');

    console.log(`Found ${offers.length} offers`);

    offers.forEach((offer, index) => {
      try {
        const providerElement = offer.querySelector('.provider-name, .company-name');
        const rateElement = offer.querySelector('.rate-amount, .price-amount');

        if (providerElement && rateElement) {
          const provider = providerElement.innerText.trim();
          const rateText = rateElement.innerText.trim();
          const rate = parseFloat(rateText.replace(/[^\d.]/g, '')) / 100; // Convert to dollars

          results.push({ provider, rate });
          console.log(`Offer ${index + 1} - Provider: ${provider}, Rate: $${rate.toFixed(5)} per kWh`);
        } else {
          console.log(`Offer ${index + 1} - Missing provider or rate element`);
        }
      } catch (e) {
        console.error(`Error parsing offer ${index + 1}:`, e);
      }
    });

    return results;
  });

  await browser.close();
  return rates;
}

const url = 'https://www.choosetexaspower.org/compare-offers/?zipCode=75212&m=moven';
scrapeRates(url)
  .then(rates => {
    console.log('Scraped rates:', JSON.stringify(rates, null, 2));
  })
  .catch(error => {
    console.error('Error:', error);
  });