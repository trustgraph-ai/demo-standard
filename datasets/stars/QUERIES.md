# Stars GraphQL Queries

## Named stars

Stars that have a proper (common) name.

```graphql
query {
  stars(where: { proper: { not: "" } }, limit: 100) {
    proper con spect mag dist lum
  }
}
```

## Stars in a constellation (e.g. Orion)

```graphql
query {
  stars(where: { con: { eq: "Ori" } }, limit: 50) {
    proper spect mag dist lum bayer flam
  }
}
```

## Look up a star by name (e.g. Sirius)

```graphql
query {
  stars(where: { proper: { eq: "Sirius" } }, limit: 1) {
    proper con spect mag dist lum ra dec ci bayer flam
  }
}
```

## Stars by spectral type (e.g. O-type)

```graphql
query {
  stars(where: { spect: { eq: "G2V" } }, limit: 50) {
    proper spect mag dist lum con
  }
}
```

## Nearest stars to Sol

Stars within 5 parsecs.

```graphql
query {
  stars(where: { dist: { lt: 5.0 } }, limit: 50) {
    proper spect mag dist lum con gl
  }
}
```

## Brightest stars by apparent magnitude

Stars brighter than magnitude 1.0.

```graphql
query {
  stars(where: { mag: { lt: 1.0 } }, limit: 50) {
    proper spect mag dist lum con bayer
  }
}
```

## Most luminous stars

Stars with luminosity greater than 10000 Solar luminosities.

```graphql
query {
  stars(where: { lum: { gt: 10000.0 } }, limit: 50) {
    proper spect mag dist lum con
  }
}
```

## Variable stars

Stars with a variable star designation.

```graphql
query {
  stars(where: { var: { not: "" } }, limit: 50) {
    proper var var_min var_max spect mag con
  }
}
```

## Stars in multiple star systems

```graphql
query {
  stars(where: { base: { not: "" } }, limit: 50) {
    proper base comp comp_primary spect mag con
  }
}
```

## Look up a star by Hipparcos ID (e.g. 32349 = Sirius)

```graphql
query {
  stars(where: { hip: { eq: 32349 } }, limit: 1) {
    proper hip hd hr spect mag dist lum con
  }
}
```
