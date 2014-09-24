#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace {

class ChecksumXorGenerator
{
public:
    ChecksumXorGenerator(uint32_t seed);
    uint32_t generate();

private:
    void initTables();
    static void initMix(uint32_t* xorvals);
    void scramble();
    static void scrambleRound(uint32_t shiftedVal, uint32_t* key0_ptr, uint32_t* key2_ptr, uint32_t** localunk_ptr, uint32_t** lc_unk0_ptr, uint32_t** lc_unk200_ptr, uint32_t** localxor_ptr, uint32_t* var_18_ptr, uint32_t* var_1c_ptr);
    static uint32_t Crazy_XOR_01(const uint32_t* data, uint32_t index);

    uint32_t counter_;
    uint32_t xorTable_[256];
    uint32_t unkTable_[256];
    uint32_t value0_;
    uint32_t value1_;
    uint32_t value2_;
};

ChecksumXorGenerator::ChecksumXorGenerator(uint32_t seed)
{
    memset(xorTable_, 0, sizeof(xorTable_));
    value0_ = seed;
    value1_ = seed;
    value2_ = seed;
    initTables();
}

uint32_t ChecksumXorGenerator::generate()
{
    uint32_t value = xorTable_[counter_];

    if(counter_ > 0)
    {
        counter_--;
    }
    else
    {
        scramble();
        counter_ = 255;
    }

    return value;
}

void ChecksumXorGenerator::initTables()
{
    uint32_t xorvals[8];

    for(int i = 0; i < 8; i++)
    {
        xorvals[i] = 0x9E3779B9;
    }

    for(int i = 0; i < 4; i++)
    {
        initMix(xorvals);
    }

    for(int i = 0; i < 256; i += 8)
    {
        for(int j = 0; j < 8; j++)
        {
            xorvals[j] += xorTable_[i + j];
        }

        initMix(xorvals);

        for(int j = 0; j < 8; j++)
        {
            unkTable_[i + j] = xorvals[j];
        }
    }

    for(int i = 0; i < 256; i += 8)
    {
        for(int j = 0; j < 8; j++)
        {
            xorvals[j] += unkTable_[i + j];
        }

        initMix(xorvals);

        for(int j = 0; j < 8; j++)
        {
            unkTable_[i + j] = xorvals[j];
        }
    }

    scramble();
    counter_ = 255;
}

void ChecksumXorGenerator::initMix(uint32_t* xorvals)
{
#define ROUND(base, shift) \
    xorvals[base] ^= xorvals[(base + 1) & 7] shift; \
    xorvals[(base + 3) & 7] += xorvals[base]; \
    xorvals[(base + 1) & 7] += xorvals[(base + 2) & 7];

    ROUND(0, << 0x0B);
    ROUND(1, >> 0x02);
    ROUND(2, << 0x08);
    ROUND(3, >> 0x10);
    ROUND(4, << 0x0A);
    ROUND(5, >> 0x04);
    ROUND(6, << 0x08);
    ROUND(7, >> 0x09);

#undef ROUND
}

void ChecksumXorGenerator::scramble()
{
    uint32_t* local_unk = unkTable_;
    uint32_t* local_xor = xorTable_;
    uint32_t key0 = value0_;
    value2_++;
    uint32_t key2 = value1_ + value2_;
    uint32_t* lc_unk0 = local_unk;
    uint32_t* lc_unk200 = lc_unk0 + 128;
    uint32_t* lc_unk0_stop_point = lc_unk200;
    uint32_t var_18;
    uint32_t var_1c;

    while(lc_unk0 < lc_unk0_stop_point)
    {
        scrambleRound(key0 << 0x0D, &key0, &key2, &local_unk, &lc_unk0, &lc_unk200, &local_xor, &var_18, &var_1c);
        scrambleRound(key0 >> 0x06, &key0, &key2, &local_unk, &lc_unk0, &lc_unk200, &local_xor, &var_18, &var_1c);
        scrambleRound(key0 << 0x02, &key0, &key2, &local_unk, &lc_unk0, &lc_unk200, &local_xor, &var_18, &var_1c);
        scrambleRound(key0 >> 0x10, &key0, &key2, &local_unk, &lc_unk0, &lc_unk200, &local_xor, &var_18, &var_1c);
    }

    lc_unk200 = local_unk;

    while(lc_unk200 < lc_unk0_stop_point)
    {
        scrambleRound(key0 << 0x0D, &key0, &key2, &local_unk, &lc_unk0, &lc_unk200, &local_xor, &var_18, &var_1c);
        scrambleRound(key0 >> 0x06, &key0, &key2, &local_unk, &lc_unk0, &lc_unk200, &local_xor, &var_18, &var_1c);
        scrambleRound(key0 << 0x02, &key0, &key2, &local_unk, &lc_unk0, &lc_unk200, &local_xor, &var_18, &var_1c);
        scrambleRound(key0 >> 0x10, &key0, &key2, &local_unk, &lc_unk0, &lc_unk200, &local_xor, &var_18, &var_1c);
    }

    value1_ = key2;
    value0_ = key0;
}

void ChecksumXorGenerator::scrambleRound(
        uint32_t shiftedVal,
        uint32_t* key0_ptr,
        uint32_t* key2_ptr,
        uint32_t** localunk_ptr,
        uint32_t** lc_unk0_ptr,
        uint32_t** lc_unk200_ptr,
        uint32_t** localxor_ptr,
        uint32_t* var_18_ptr,
        uint32_t* var_1c_ptr)
{
    *var_18_ptr = **lc_unk0_ptr;
    *key0_ptr = (*key0_ptr ^ shiftedVal) + **lc_unk200_ptr;
    *lc_unk200_ptr = *lc_unk200_ptr + 1;
    uint32_t res = Crazy_XOR_01(*localunk_ptr, *var_18_ptr);
    *var_1c_ptr = res + *key0_ptr + *key2_ptr;
    **lc_unk0_ptr = *var_1c_ptr;
    *lc_unk0_ptr = *lc_unk0_ptr + 1;
    res = Crazy_XOR_01(*localunk_ptr, *var_1c_ptr >> 8);
    *key2_ptr = res + *var_18_ptr;
    **localxor_ptr = *key2_ptr;
    *localxor_ptr = *localxor_ptr + 1;
}

uint32_t ChecksumXorGenerator::Crazy_XOR_01(const uint32_t* data, uint32_t index)
{
    return *(const uint32_t*)((const uint8_t*)data + (index & 0x3FC));
}

} // unnamed namespace

extern "C" void* generator_create(uint32_t seed)
{
    return new ChecksumXorGenerator(seed);
}

extern "C" void generator_destroy(void* handle)
{
    ChecksumXorGenerator* generator = reinterpret_cast<ChecksumXorGenerator*>(handle);
    delete generator;
}

extern "C" uint32_t generator_generate(void* handle)
{
    ChecksumXorGenerator* generator = reinterpret_cast<ChecksumXorGenerator*>(handle);
    return generator->generate();
}

#ifdef TEST

const uint32_t seeds[] =
{
    0x6da1258d, 0x9bd62802
};

const uint32_t results[][128] =
{
    {
        0x0ba3a3c1,
        0xda105a56,
        0x993220e1,
        0x1cd174e6,
        0x2d7d4c73,
        0x5e715cda,
        0xe9408bd2,
        0xf25b2601,
        0x2d0021ae,
        0xd39793f6,
        0x9a52df24,
        0xf99b44a2,
        0x30a21532,
        0xa675801a,
        0x7c0d78ce,
        0x5256bb81,
        0x60cb23e6,
        0xb131d2cb,
        0x5d06db46,
        0x23256fbb,
        0xcd4d8a35,
        0x49d557ac,
        0xc8a88cc9,
        0x0a145ca5,
        0x2c888ff1,
        0x93619d0c,
        0x3667d426,
        0x322e7080,
        0xeabc789a,
        0x50b03ab4,
        0xd6627a76,
        0xf163e0ee,
        0xba33032f,
        0x6bbd5129,
        0xa71183dc,
        0x0096528c,
        0xd2caa801,
        0x75777925,
        0x4dafd206,
        0xd542ee08,
        0x208eb4f1,
        0xd07cb57c,
        0xdf4570b5,
        0x04fda0e7,
        0x9f3d5181,
        0x4bfcfe36,
        0x39a4085c,
        0xb7c369ec,
        0xeeeb7a11,
        0x1bd6bea0,
        0x0e30995f,
        0xb14a481e,
        0x4e6d8121,
        0x6f85f882,
        0xbab1924d,
        0x7254484e,
        0xef228980,
        0xa0ef1f86,
        0x0895fdaa,
        0x44c19354,
        0x28358d88,
        0xb7461b4c,
        0xf03f07d9,
        0xa465c76b,
        0x99827e7e,
        0xfd88592d,
        0xfb80cf3f,
        0xc263e9a2,
        0x172bb400,
        0x84d24428,
        0x071e8f54,
        0x6129c7ff,
        0x92d8aac8,
        0x32eb3816,
        0xe6425a01,
        0x744f2314,
        0xab0a742d,
        0x241db7bd,
        0x5655d248,
        0x66c97ce0,
        0x89cd69f0,
        0x22aa9d50,
        0xd8493826,
        0xd37e1284,
        0xeb4fb665,
        0x07dc817b,
        0xfdcbf3e4,
        0x15d647b6,
        0x2cd20e66,
        0x9bd5d96b,
        0x99096c89,
        0xa34725af,
        0x96fd0508,
        0xf6cf6629,
        0x90141b01,
        0x68745e38,
        0x8e155a4e,
        0x2ae05602,
        0x76347981,
        0x2c0943b7,
        0xe44b0293,
        0xc200d710,
        0xa978efaa,
        0xf05762ec,
        0x237efe46,
        0x15607ab1,
        0x41dafb51,
        0x7d61ffdc,
        0xa6447867,
        0x84e849cd,
        0xb4a680cb,
        0x569313ae,
        0xe2fc5a3d,
        0x9277f7b3,
        0xef7ee78e,
        0xb9c18bd9,
        0x2e05c90d,
        0xb3fc5c66,
        0xa810691a,
        0xa2339b13,
        0x6fcf0fd0,
        0xb0fa0437,
        0xb310d06e,
        0x1d229f23,
        0x360af893,
        0x4833e789,
        0x6e4ccab0,
        0x81332704
    },
    {
        0x37173653,
        0x95cd9dee,
        0x741766ef,
        0xda8b238d,
        0xefe4f9b5,
        0xeb2deb7b,
        0x08e6d615,
        0x730ed4a6,
        0x1fcfd43b,
        0xb1914e04,
        0x49f8d4a0,
        0x16696df0,
        0x75b6c6d2,
        0x858fa8f2,
        0xa5a22f15,
        0x9355ebea,
        0xc576c86c,
        0x376db21a,
        0x6dc9ea44,
        0xaca4cc06,
        0x4cb5da0b,
        0x31987b46,
        0x41dfa2b3,
        0x09b5d3d0,
        0x70a783d3,
        0x8c30aa8f,
        0x3873cc90,
        0x6d1561b0,
        0x3e7fa45e,
        0xbb0d2e17,
        0x4d83bab8,
        0x0dbf0f21,
        0x1b36c9ee,
        0xd278e72b,
        0xc03da70f,
        0x0a9b8a62,
        0xf4d47767,
        0x4e1c4b6a,
        0x5b794edf,
        0xda52e741,
        0x90df5b9c,
        0x19f40af5,
        0x2ecd6677,
        0x0ba96304,
        0x4c3231ba,
        0x35088047,
        0xb2b24966,
        0xb8ba8c9f,
        0x9e54e29a,
        0xe149647e,
        0x3855a994,
        0x0631b8ac,
        0xfbed7f09,
        0x48ada66d,
        0x8535ecdb,
        0x6c4c8b1d,
        0xc466116e,
        0xc16ea7f0,
        0x60713ab5,
        0x13357aba,
        0xb7d72df9,
        0x95a6433f,
        0x63ffcab1,
        0xd8b62f61,
        0x7c413d71,
        0x7f662970,
        0x431e4478,
        0x76f12b33,
        0xc461b72b,
        0x47d58be6,
        0x06a65bf8,
        0xa97f66f0,
        0x6a9d1ea6,
        0xe8e8590b,
        0x81b58b08,
        0x12fde8f0,
        0xaf7c1f08,
        0x40cd70ca,
        0xd62e0872,
        0x40684fe4,
        0xf0f0a1b3,
        0x974c8c58,
        0xf459bfed,
        0xe0471175,
        0x143d2ad1,
        0x7ff940a1,
        0xeaf01848,
        0xd7eb1796,
        0x89615427,
        0x88ab9b9c,
        0xb57e3254,
        0x4772e8cf,
        0x6236e5af,
        0xc5077617,
        0x612e67a9,
        0x963d17a5,
        0xb3d2b936,
        0xc0883720,
        0x982db3dd,
        0x4bb15f13,
        0x4f4d5b9e,
        0x638d7c15,
        0x63289d5b,
        0x477f900f,
        0x44d5ae37,
        0x554e2ade,
        0xa6f8d189,
        0x71fb7f46,
        0x71ed9de7,
        0x1341a1f7,
        0x1a841467,
        0xb4457d50,
        0x5eba209c,
        0x32283557,
        0xe291cc00,
        0x1164215f,
        0x64f61c62,
        0x8b5b5d52,
        0xf2edd30c,
        0xc0cc8c93,
        0x448fd560,
        0x14744337,
        0x6ec47869,
        0xaecad205,
        0xaafbdefd,
        0x04374702,
        0xc0fc609e,
        0x12d8a8a1
    }
};

int main(int argc, char** argv)
{
    int nfailures = 0;

    for(int i = 0; i < sizeof(seeds)/sizeof(seeds[0]); i++)
    {
        ChecksumXorGenerator generator(seeds[i]);

        for(int j = 0; j < sizeof(results[0])/sizeof(results[0][0]); j++)
        {
            uint32_t actual = generator.generate();
            uint32_t expected = results[i][j];

            if(actual != expected)
            {
                nfailures++;
            }
        }
    }

    if(nfailures != 0)
    {
        fprintf(stderr, "nfailures = %d\n", nfailures);
        return EXIT_FAILURES;
    }

    return EXIT_SUCCESS;
}

#endif

