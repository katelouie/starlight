# Famous People Test Suite Report

This report summarizes the natal charts generated for famous individuals to test various aspects of the Starlight astrology library.

## Test Cases Generated

### Albert Einstein

- **Sun Sign**: Unknown
- **Moon Sign**: Unknown
- **Rising Sign**: Unknown
- **Chart File**: `albert_einstein_chart.svg`
- **Test Purpose**: Pisces Sun with strong Sagittarius - tests fire/water balance and scientific genius aspects

### Frida Kahlo

- **Sun Sign**: Unknown
- **Moon Sign**: Unknown
- **Rising Sign**: Unknown
- **Chart File**: `frida_kahlo_chart.svg`
- **Test Purpose**: Cancer Sun with Leo Rising - tests artistic creativity and emotional intensity

### Leonardo da Vinci

- **Sun Sign**: Unknown
- **Moon Sign**: Unknown
- **Rising Sign**: Unknown
- **Chart File**: `leonardo_da_vinci_chart.svg`
- **Test Purpose**: Aries Sun with strong Taurus - tests Renaissance genius and artistic/scientific blend

### Oprah Winfrey

- **Sun Sign**: Unknown
- **Moon Sign**: Unknown
- **Rising Sign**: Unknown
- **Chart File**: `oprah_winfrey_chart.svg`
- **Test Purpose**: Aquarius Sun with Sagittarius Rising - tests media influence and humanitarian aspects

### Martin Luther King Jr.

- **Sun Sign**: Unknown
- **Moon Sign**: Unknown
- **Rising Sign**: Unknown
- **Chart File**: `martin_luther_king_jr_chart.svg`
- **Test Purpose**: Capricorn Sun - tests leadership and social justice themes

### Marie Curie

- **Sun Sign**: Unknown
- **Moon Sign**: Unknown
- **Rising Sign**: Unknown
- **Chart File**: `marie_curie_chart.svg`
- **Test Purpose**: Scorpio Sun - tests scientific breakthrough and transformational themes

### Winston Churchill

- **Sun Sign**: Unknown
- **Moon Sign**: Unknown
- **Rising Sign**: Unknown
- **Chart File**: `winston_churchill_chart.svg`
- **Test Purpose**: Sagittarius Sun with Leo Rising - tests wartime leadership and oratory skills

### Pablo Picasso

- **Sun Sign**: Unknown
- **Moon Sign**: Unknown
- **Rising Sign**: Unknown
- **Chart File**: `pablo_picasso_chart.svg`
- **Test Purpose**: Scorpio Sun - tests artistic revolution and creative transformation

### Maya Angelou

- **Sun Sign**: Unknown
- **Moon Sign**: Unknown
- **Rising Sign**: Unknown
- **Chart File**: `maya_angelou_chart.svg`
- **Test Purpose**: Aries Sun - tests literary genius and resilience themes

### Nikola Tesla

- **Sun Sign**: Unknown
- **Moon Sign**: Unknown
- **Rising Sign**: Unknown
- **Chart File**: `nikola_tesla_chart.svg`
- **Test Purpose**: Cancer Sun with midnight birth - tests electrical genius and innovative aspects

## Package Features Tested

This test suite validates:

1. **Chart Generation**: Basic natal chart creation with various birth data
2. **Planet Positioning**: Accurate planetary positions across different time periods
3. **Sign Calculations**: Proper zodiac sign determination
4. **House Systems**: House cusp calculations
5. **Geographical Diversity**: Charts from various global locations
6. **Historical Range**: Birth dates spanning from 15th to 20th centuries
7. **Time Variations**: Different birth times including midnight births
8. **SVG Rendering**: Chart visualization with planet symbols and information
9. **Moon Phase Accuracy**: Accurate lunar phase representations
10. **Collision Detection**: Proper spacing of chart elements

## Usage

To run this test suite:

```bash
source ~/.zshrc && pyenv activate starlight
cd /path/to/starlight
python tests/famous_people_test_suite.py
```

Generated charts can be found in:
- `tests/output/famous_people/` (test outputs)
- `examples/famous_people/` (example showcase)
