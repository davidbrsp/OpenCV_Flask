function divShow( expr ) {

  // const expr = 'Papayas';
  // document.getElementById("delete").style.display = "block";
  console.log( expr );
  switch ( expr ) {
    case 'divcrop':
      document.getElementById( "divcrop"     ).style.display = "block";
      document.getElementById( "divdelete"   ).style.display = "none";      
      document.getElementById( "divbinarize" ).style.display = "none";  
      break;
    case 'divdelete' :
      document.getElementById( "divcrop"     ).style.display = "none";
      document.getElementById( "divdelete"   ).style.display = "block";      
      document.getElementById( "divbinarize" ).style.display = "none";  
      break;
    case 'divbinarize' :
      document.getElementById( "divcrop"     ).style.display = "none";
      document.getElementById( "divdelete"   ).style.display = "none";      
      document.getElementById( "divbinarize" ).style.display = "block";  
      break;
    default:
      console.log(`Sorry, can't understand ${ expr }.`);
  }
  





 
}