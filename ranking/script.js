async function loadPlayerLibrary() {
    const request = new Request("player_ranking.json");
    const response = await fetch(request);

    return await response.json();
}

async function generateRankingTable() {
    playerData = await loadPlayerLibrary();

    let table = document.getElementById("ranking-table");

    for (var index in playerData) {
        let tboddy = table.createTBody();
        row = tboddy.insertRow();
        let cell = row.insertCell();
        text = document.createTextNode(index);
        cell.appendChild(text); 
    
        cell = row.insertCell();
        text = document.createTextNode(playerData[index][0]);
        cell.appendChild(text); 
    
        cell = row.insertCell();
        text = document.createTextNode(playerData[index][1]);
        cell.appendChild(text); 
    
        cell = row.insertCell();
        text = document.createTextNode(playerData[index][2]);
        cell.appendChild(text); 
    }
}

generateRankingTable();