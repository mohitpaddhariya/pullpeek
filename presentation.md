---
layout: cover
---
# Increasing SQL Package Test Coverage
## PR #21384: From 35% to 75%

---
layout: default
---
# Overview

- Comprehensive unit tests added to the `sql` package.
- Significantly increased code coverage.
- Tests cover output type handling, option validation, and application of multiple options.

---
layout: default
---
# Key Changes

- Added `TestOutputType`: Verifies correct handling of the `OutputType` option (with and without components).
- Added `TestTransform`: Ensures `Transform` function panics when output type is not specified.
- Added `TestMultipleOptions`: Validates correct application of multiple options (Input, Dialect, ExpansionAddr, OutputType).
- Increased code coverage from 35% to 75%.

---
layout: default
---
# Impact

- Improved reliability and maintainability of the `sql` package.
- Increased test coverage.
- No breaking changes introduced.

---
layout: default
---
# Example: TestMultipleOptions

Demonstrates applying and verifying multiple options simultaneously.

```go
func TestMultipleOptions(t *testing.T) {
	o := &options{
		inputs: make(map[string]beam.PCollection),
	}

	p := beam.NewPipeline()
	s := p.Root()
	col := beam.Create(s, 1, 2, 3)
	name := "test"
	dialect := "zetasql"
	addr := "localhost:8080"
	typ := reflect.TypeOf(int64(0))
	customOpt := sqlx.Option{Urn: "test"}

	// Apply multiple options
	opts := []Option{
		Input(name, col),
		Dialect(dialect),
		ExpansionAddr(addr),
		OutputType(typ),
	}

	// Apply all options
	for _, opt := range opts {
		opt(o)
	}
	o.Add(customOpt)

	// Verify all fields
	if _, ok := o.inputs[name]; !ok {
		t.Error("Input option not applied correctly")
	}
	if o.dialect != dialect {
		t.Error("Dialect option not applied correctly")
	}
	if o.expansionAddr != addr {
		t.Error("ExpansionAddr option not applied correctly")
	}
	if !reflect.DeepEqual(o.outType, typex.New(typ)) {
		t.Error("OutputType option not applied correctly")
	}
	if len(o.customs) != 1 {
		t.Error("Custom option not applied correctly")
	}
}
```