const puppeteer = require('puppeteer');

async function scrapeRates(url) {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: 'networkidle2' });

  // Adding debug information
  console.log(`Navigated to ${url}`);

  // Log the entire page content for debugging
  const pageContent = await page.content();
  console.log("Page content loaded");

  // Save the page content to a file for offline inspection
  const fs = require('fs');
  fs.writeFileSync('page-content.html', pageContent);
  console.log("Page content saved to page-content.html");

  // Adjust the selectors based on the website structure
  const rates = await page.evaluate(() => {
    const results = [];
    const offers = document.querySelectorAll('.rate-card'); // Adjust selector

    console.log(`Found ${offers.length} offers`);

    offers.forEach((offer, index) => {
      try {
        const providerElement = offer.querySelector('.provider-name'); // Adjust selector
        const rateElement = offer.querySelector('.rate-amount'); // Adjust selector

        // Debug: log the HTML content
        console.log(`Offer ${index + 1} HTML:`, offer.innerHTML);

        if (providerElement && rateElement) {
          const provider = providerElement.innerText.trim();
          const rateText = rateElement.innerText.trim();
          const rate = parseFloat(rateText.replace('¢', '').replace('/kWh', '').trim()) / 100; // Convert to dollars

          results.push({ provider, rate });

          // Debug: log extracted data
          console.log(`Offer ${index + 1} - Provider: ${provider}, Rate: $${rate.toFixed(5)} per kWh`);
        } else {
          console.error(`Offer ${index + 1} - Missing provider or rate element`);
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
