export interface Team {
    name: string;
    logo: string;
}

export const teams: Team[] = [
    { name: 'Real Madrid', logo: '/team/realmadrid.png' },
    { name: 'Barcelona', logo: '/team/barca.png' },
    { name: 'Atlético Madrid', logo: '/team/atm.png' },
    { name: 'Atalanta', logo: '/team/atalanta.png' },
    { name: 'Bayern Munich', logo: '/team/bayern.png' },
    { name: 'Borussia Dortmund', logo: '/team/dortmund.png' },
    { name: 'Bayer Leverkusen', logo: '/team/leverkusen.png' },
    { name: 'Eintracht Frankfurt', logo: '/team/frankfurt.png' },
    { name: 'Arsenal', logo: '/team/arsenal.png' },
    { name: 'Manchester City', logo: '/team/city.png' },
    { name: 'Manchester United', logo: '/team/mu.png' },
    { name: 'Chelsea', logo: '/team/chelsea.png' },
    { name: 'Liverpool', logo: '/team/Liverpool.png' },
    { name: 'Tottenham Hotspur', logo: '/team/spurs.png' },
    { name: 'Newcastle United', logo: '/team/newcastle.png' },
    { name: 'Atletic Bilbao', logo: '/team/bilbao.png' },
    { name: 'Juventus', logo: '/team/juven.png' },
    { name: 'Napoli', logo: '/team/napoli.png' },
    { name: 'Inter Milan', logo: '/team/inter.png' },
    { name: 'Paris Saint-Germain', logo: '/team/psg.png' },
    { name: 'Marseille', logo: '/team/marseille.png' },
    { name: 'Monaco', logo: '/team/monaco.png' },
    { name: 'Club Brugge', logo: '/team/brudge.png' },
    { name: 'Ajax', logo: '/team/ajax.png' },
    { name: 'PSV', logo: '/team/psv.png' },
    { name: 'Benfica', logo: '/team/benfica.png' },
    { name: 'Sporting CP', logo: '/team/sporting.png' },
    { name: 'Galatasaray', logo: '/team/galatasaray.png' },
    { name: 'Olympiacos', logo: '/team/olymp.png' },
    { name: 'Slavia Praha', logo: '/team/slavia.png' },
    { name: 'Union Saint-Gilloise', logo: '/team/union.png' },
    { name: 'Villarreal', logo: '/team/villareal.png' },
    { name: 'FC København', logo: '/team/fc.png' },
    { name: 'FC Porto', logo: '/team/porto.png' },
];

export function getTeamLogo(name: string): string | undefined {
    return teams.find((t) => t.name.toLowerCase() === name.toLowerCase())?.logo;
}