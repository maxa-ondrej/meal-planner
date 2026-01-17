from bs4 import BeautifulSoup, Tag
from fingrlix.models import Food
from fingrlix.errors import NoMenuFoundError, FoodCardParseError

nutrition_labels = ["Kalorie", "Tuky", "Sacharidy", "Bílkoviny"]

def parse_to_menu(soup: BeautifulSoup):
    section = soup.find("section", id="foods")
    if not section:
        raise NoMenuFoundError("No menu section found in the HTML.")
    foods = section.find_all("div", class_="food-card")
    if not foods:
        raise NoMenuFoundError("No food cards found in the menu section.")
    foods_list: list[Food] = []
    for food in foods:
        try:
            parsed_food = _parse_food_card(food)
            foods_list.extend(parsed_food)
        except FoodCardParseError as e:
            print(f"Warning: Skipping a food card due to parse error: {e}")
    return foods_list

def _parse_food_card(soup: Tag) -> list[Food]:
    wrapper = soup.find("div", class_="food-card-image-wrapper")
    if not wrapper:
        raise FoodCardParseError("No image wrapper found in food card.")
    image_tag = wrapper.find("img")
    if not image_tag or not image_tag.get("src"):
        raise FoodCardParseError("No image found in food card.")
    image = str(image_tag["src"])
    
    subtitle = soup.find(class_="food-card-subtitle")
    if not subtitle:
        raise FoodCardParseError("No subtitle found in food card.")
    type = subtitle.get_text(strip=True)
    
    name_tag = soup.find(class_="food-card-title")
    if not name_tag:
        raise FoodCardParseError("No title found in food card.")
    name = name_tag.get_text(strip=True)
    
    description_tag = soup.find(class_="food-card-description")
    if not description_tag:
        raise FoodCardParseError("No description found in food card.")
    description = description_tag.get_text(strip=True)
    
    food_portions = soup.find_all("div", class_="food-portion-card")
    if not food_portions:
        raise FoodCardParseError("No food portions cards found in food card.")
    
    foods: list[Food] = []
    for food_portion in food_portions:
        cols = food_portion.find_all("div", recursive=False)
        if len(cols) != 3:
            raise FoodCardParseError("Unexpected number of columns in food portion card.")
        
        variant_span = cols[0].find("span", recursive=False)
        if not variant_span:
            raise FoodCardParseError("No variant found in food portion card.")
        variant = variant_span.get_text(strip=True)
        
        price_span = cols[0].find("span", class_="price")
        if not price_span:
            raise FoodCardParseError("No price found in food portion card.")
        price_text = price_span.get_text(strip=True).replace("Kč", "").strip()
        try:
            price = int(price_text)
        except ValueError:
            raise FoodCardParseError(f"Invalid price format: {price_text}")
        
        nutrition_div = cols[1].find("div", class_="tooltip-content")
        if not nutrition_div:
            raise FoodCardParseError("No nutrition info found in food portion card.")
        nutrition_block = nutrition_div.find("p", recursive=False)
        if not nutrition_block:
            raise FoodCardParseError("No nutrition block found in food portion card.")
        try:
            nutritions = [
                span.get_text(strip=True) for span in nutrition_block.find_all("span", recursive=False)
            ]
            if len(nutritions) != 5:
                raise FoodCardParseError(f"Unexpected number of nutrition values found: {len(nutritions)}")
            nutritions_dict = {label: int(value.removeprefix(label + ": ").split(" ")[0]) for label, value in zip(nutrition_labels, nutritions)}
            calories = nutritions_dict["Kalorie"]
            fat = nutritions_dict["Tuky"]
            carbohydrates = nutritions_dict["Sacharidy"]
            protein = nutritions_dict["Bílkoviny"]
        except (ValueError, IndexError) as e:
            raise FoodCardParseError(f"Invalid nutrition format") from e
        
        foods.append(
            Food(
                name=name,
                variant=variant,
                type=type,
                description=description,
                image=image,
                price=price,
                calories=calories,
                fat=fat,
                carbohydrates=carbohydrates,
                protein=protein,
            )
        )
    
    return foods
    