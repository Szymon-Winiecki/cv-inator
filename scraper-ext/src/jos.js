
offerScrapper = new TheProtocolItScraper();

alert("Click 's' to scrap loaded offer.\n" + offerScrapper.getUsageInstructions() + "\nYou can find the result in conslole and in your clipboard.");

document.body.addEventListener("keyup", (e) => {
    if (e.key === "s") {
        const offer = offerScrapper.scrapLoaded();
        console.log(offer);
        navigator.clipboard.writeText(offer);
    }
});