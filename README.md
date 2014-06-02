# Binarize
Binarize is going to be an efficient, small and flexible binary serialization format. It will support serialization of dynamic objects, like lists or Hashtables as well as custom objects. It's still under heavy development and cannot be considered stable.

## Example
```python
class TestEnum(enum.Enum):
    TEST1 = 'string'
    TEST2 = ('tuple', 1, 2, 3)

class Test1(binarize.Structure):
    field1 = binarize.UINT8
    field2 = binarize.STRING(size=20)
    field3 = binarize.UUID

class Test2(Test1):
    field4 = TestEnum
    
class Test3(binarize.Structure):
    test2 = Test2
    abc = binarize.STRING(size=3)
```

```
<Structure:Test1 [<Field name="field1", type="<Primitive:UINT8>">,
                  <Field name="field2", type="<Primitive:STRING, size=20>">,
                  <Field name="field3", type="<Primitive:UUID>">]>
<Structure:Test2 [<Field name="field1", type="<Primitive:UINT8>">,
                  <Field name="field2", type="<Primitive:STRING, size=20>">,
                  <Field name="field3", type="<Primitive:UUID>">,
                  <Field name="field4", type="<Enum:TestEnum>">]>
<Structure:Test3 [<Field name="test2", type="<StructureType:Test2 [
                      <Field name="field1", type="<Primitive:UINT8>">,
                      <Field name="field2", type="<Primitive:STRING, size=20>">,
                      <Field name="field3", type="<Primitive:UUID>">,
                      <Field name="field4", type="<Enum:TestEnum>">]>">,
                  <Field name="abc", type="<Primitive:STRING, size=3>">]>

<Structure:Test1 field1="34", field2="abcdef",
                 field3="3550d7e7-ec96-4b09-a233-8ab2e11e4230">
--> b'"abcdef              5P\xd7\xe7\xec\x96K\t\xa23\x8a\xb2\xe1\x1eB0'

<Structure:Test2 field1="255", field2="abc123",
                 field3="65501639-9f0c-4faf-8f55-11e568d7b6f5",
                 field4="TestEnum.TEST2">
--> (b'\xffabc123              eP\x169\x9f\x0cO\xaf\x8fU\x11\xe5h\xd7\xb6\xf5'
     b'\x01')
     
<Structure:Test3 test2="<Structure:Test2 field1="255", field2="abc123",
                            field3="65501639-9f0c-4faf-8f55-11e568d7b6f5",
                            field4="TestEnum.TEST2">",
                 abc="abc">
--> (b'\xffabc123              eP\x169\x9f\x0cO\xaf\x8fU\x11\xe5h\xd7\xb6\xf5'
     b'\x01abc')

```

## Specification
### Dynamic Serialization Format
    Constructor Codes:
    0b000           -> Positive 5-Bit Integer
    0b001           -> Negative 5-Bit Integer
    0b010           -> String (5-Bit Length)
    0b011           -> Bytes (5-Bit Length)
    0b100           -> List (5-Bit Length)
    0b101           -> Hashtable (5-Bit Length)
    0b110
         00         -> Fixed Width Integer
           00           -> 8-Bit Integer
             0              -> Positive
             1              -> Negative
           01           -> 16-Bit Integer
             0              -> Positive
             1              -> Negative
           10           -> 32-Bit Integer
             0              -> Positive
             1              -> Negative
           11           -> 64-Bit Integer
             0              -> Positive
             1              -> Negative
         01
           000      -> Float (32-Bit)
           001      -> Double (64-Bit)
           010      -> 32-Bit Decimal
           011      -> 64-Bit Decimal
           100      -> 128-Bit Decimal
           101      -> True
           110      -> False
           111      -> None
         10
           00       -> Variable Length Integer
             0          -> Positive
             1          -> Negative
           01
             0      -> UUID
             1      -> END
           10
             0      -> IPV4
             1      -> IPV6
           11
             0      -> DATE
             1      -> TIME
         11
           0        -> String
            00          -> 8-Bit Length
            01          -> 16-Bit Length
            10          -> 32-Bit Length
            11          -> 64-Bit Length
           1        -> Bytes
            00          -> 8-Bit Length
            01          -> 16-Bit Length
            10          -> 32-Bit Length
            11          -> 64-Bit Length
    0b111
         0
          0
           000      -> DATETIME
           001      -> Regular Expression
           010      -> POINTER
           ...      -> reserved
          1
           0        -> Described Type
            00          -> 8-Bit Integer
            01          -> 16-Bit Integer
            10          -> 8-Bit Name
            11          -> 16-Bit Name
           1        -> Custom Type
            00          -> by 8-Bit Integer
            01          -> by 16-Bit Integer
            10          -> by Name (8-Bit Length)
            11          -> by Name (16-Bit Length)
         1          -> Blocks
          0
           0            -> Compressed (Default Options)
            00              -> DEFLATE
            10              -> GZIP
            01              -> LZMA
            11              -> Custom
          0
           1            -> Encrypted (Option Byte Follows)
            00              -> AES
            01              -> reserved
            10              -> reserved
            11              -> Custom
          1             -> Signed
           0                -> reserved
           1                -> reserver 
            00              -> ECDSA
            01              -> reserved
            10              -> reserved
            11              -> Custom

    Variable Length Integer (little endian encoded):
        0b0         -> No More Bytes
        0b1         -> Bytes Follow

    Length Encoding (0 to 590295810496146710655):
        0b0         -> 0 Bytes Follow (0 to 127)
        0b1         -> Length Bytes Follow 
           00       -> 8-Bit Length Follows (128 to 8319)
           01       -> 16-Bit Length Follows (8320 to 2105471)
           10       -> 32-Bit Length Follows (2105472 to 137441058943)
           11       -> 64-Bit Length Follows (137441058944 to 590295810496146710655)

    Date Format:
        Bit  1 -  5     -> Day (1 - 31)
        Bit  6 -  9     -> Month (1 - 12)
        Bit 10 - 15     -> Year (1 - 9999)

    Time Format:
        Bit  1 -  5     -> Hour (0 - 23)
        Bit  6 - 11     -> Minutes (0 - 59)
        Bit 12 - 17     -> Seconds (0 - 59)
        Bit 18          -> with Microsecond
        Bit 19          -> with Timezone
        
        Microsecond (0 - 999999):
            Bit 20 - 40
        
        Timezone (UTC offset in Minutes):
            With Microsecond:
                Bit 41          -> Offset Sign
                Bit 42 - 56     -> Minutes (0 - 1439)
            Without Microsecond:
                Bit 25          -> Offset Sign
                Bit 26 - 40     -> Minutes (0 - 1439)
