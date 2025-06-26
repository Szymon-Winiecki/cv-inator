class TheProtocolItScraper extends Scraper {
    constructor() {
        super();
    }

    getUsageInstructions() {
        return "You have to click on the offer to load it.";
    }

    init() {
        
    }

    scrapLoaded() {
        return this.#scrapOffer();
    }

    #fieldExtractor = new Map([
        ["offer_title", () => this.#scrapOfferTitle()],
        ["company", () => this.#scrapCompany()],
        ["salary", () => this.#scrapSalary()],
        ["contract", () => this.#scrapContract()],
        ["location", () => this.#scrapLocation()],
        ["experience", () => this.#scrapExperienceLevel()],
        ["expected_technologies", () => this.#scrapExpectedTechnologies()],
        ["optional_technologies", () => this.#scrapOptionalTechnologies()],
        ["offer_content", () => this.#scrapOfferContent()],
    ])
    
    #scrapOfferTitle() {
        const selected = document.querySelector(".t1yrx4v1");
        return selected ? selected.textContent : "N/A";
    }
    
    #scrapCompany() {
        const selected = document.querySelector(".c1vxjvoe");
        return selected ? selected.textContent : "N/A";
    
    }
    
    #scrapSalary() {
        const selected = document.querySelector(".ss7yptf");
        return selected ? selected.textContent : "N/A";
    }
    
    #scrapContract() {
        const selected = document.querySelector(".c1l2iy6w");
        return selected ? selected.textContent : "N/A";
    }
    
    #scrapLocation() {
        const workTypeSelected =  document.querySelector("div.s1bu9jax:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1)");
        const locationSelected =  document.querySelector("div.s1bu9jax:nth-child(4) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1)");
    
        if (workTypeSelected && locationSelected) {
            return `${workTypeSelected.textContent} - ${locationSelected.textContent}`;
        }
        else if (workTypeSelected) {
            return workTypeSelected.textContent;
        }
        else if (locationSelected) {
            return locationSelected.textContent;
        }
        else {
            return "N/A";
        }
    }
    
    #scrapExperienceLevel() {
        const selected =  document.querySelector("div.s1bu9jax:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1)");
        return selected ? selected.textContent : "N/A";
    }
    
    
    #findRequirementSecion(requirementType){
        const requirementsSectionSelected = document.querySelector("#TECHNOLOGY_AND_POSITION > div:nth-child(1)");
        if (!requirementsSectionSelected) {
            return "N/A";
        }
    
        let result = "N/A";
    
        requirementsSectionSelected.querySelectorAll("div").forEach((section) => {
            const type = section.querySelector("p")
            if (type && type.textContent === requirementType) {
                result = Array.from(section.querySelectorAll("span")).map((span) => span.textContent).join(", ");
                return;
            }
        });
    
        return result;
    }
    
    #scrapExpectedTechnologies() {
        let result = this.#findRequirementSecion("Wymagane");
        if (result === "N/A") {
            result = this.#findRequirementSecion("Expected");
        }
        return result;
    }
    
    #scrapOptionalTechnologies() {
        let result = this.#findRequirementSecion("Mile widziane");
        if (result === "N/A") {
            result = this.#findRequirementSecion("Optional");
        }
        return result;
    }
    
    #scrapList(section) {
        let result = "";
    
        const headerElement = section.querySelector("p");
        if (headerElement) {
            result += `${headerElement.textContent}: \n`;
        }
    
        section.querySelectorAll("li").forEach((li) => {
            result += ` - ${li.textContent}\n`;
        });
    
        return result;
    }
    
    #scrapSection(section) {
        let result = "";
    
        const headerElement = section.querySelector("p");
        if (headerElement) {
            result += `${headerElement.textContent}: \n`;
        }
    
        section.querySelectorAll("div").forEach((div) => {
            result += `${div.textContent}\n`;
        });
    
        return result;
    }
    
    #scrapColumn(selector) {
        let result = "";
        document.querySelectorAll(`${selector} > div`).forEach((section) => {
            if (section.querySelector("p")?.textContent === "Technologies we use" || section.querySelector("p")?.textContent === "Technologie, których używamy") {
               return;
            }
    
            if(section.querySelector("ul")){
                result += this.#scrapList(section) + '\n';
            }
            else {
                result += this.#scrapSection(section) + "\n";
            }
        });
    
        return result;
    }
    
    #scrapOfferContent() {
        let result = "\n";
        result += this.#scrapColumn("#TECHNOLOGY_AND_POSITION");
        result += this.#scrapColumn("#PROGRESS_AND_BENEFITS");
    
        return result;
    }
    
    
    #scrapOffer() {
        let offer = new Map();
        
        for (const [key, value] of this.#fieldExtractor) {
            offer.set(key, value());
        }
    
        return offer;
    }
}