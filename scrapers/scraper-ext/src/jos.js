
function EncapsulateScrappedOffer(offer) {
    let result = new Map();
    result.set("offer", Object.fromEntries(offer));
    result.set("source", window.location.href);
    result.set("timestamp", new Date().toISOString());
    return result;
}


function main(){
    offerScrapper = new TheProtocolItScraper();

    alert("Click 's' to scrap loaded offer.\n" + offerScrapper.getUsageInstructions() + "\nYou can find the result in conslole and in your clipboard.");

    document.body.addEventListener("keyup", (e) => {
        if (e.key === "s") {
            const offer = offerScrapper.scrapLoaded();
            const result = EncapsulateScrappedOffer(offer);
            const json = JSON.stringify(Object.fromEntries(result), null, 2);
            console.log(json);
            navigator.clipboard.writeText(json);
        }
    });
}

main();

