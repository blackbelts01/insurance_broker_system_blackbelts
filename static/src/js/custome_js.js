document.getElementsByClassName("o_control_panel")[0].style="display: none;"
document.querySelectorAll(".oe_secondary_menu li ul li").forEach(function(x){x.addEventListener("click",function(){console.log("clicked");if(document.querySelector(".oe_secondary_menu li.active a").getAttribute("data-menu-name")=="Dashboard"){document.getElementsByClassName("o_control_panel")[0].style="display: flex;"}})
})

