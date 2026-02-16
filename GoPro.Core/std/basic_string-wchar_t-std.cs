using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace std
{
	[StructLayout(LayoutKind.Sequential, Size = 32)]
	[NativeCppClass]
	[UnsafeValueType]
	internal struct basic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E
	{
		private long _003Calignment_0020member_003E;

		[SpecialName]
		public unsafe static void _003CMarshalCopy_003E(basic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E* A_0, basic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E* A_1)
		{
			if (A_0 != null)
			{
				_003CModule_003E.std_002Ebasic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E_002E_007Bctor_007D(A_0, A_1);
			}
		}

		[SpecialName]
		public unsafe static void _003CMarshalDestroy_003E(basic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E* A_0)
		{
			try
			{
				_003CModule_003E.std_002Ebasic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E_002E_Tidy_deallocate(A_0);
				return;
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((System.UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(System.UIntPtr/*delegate*<_Compressed_pair<std::allocator<wchar_t>,std::_String_val<std::_Simple_types<wchar_t> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cwchar_t_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cwchar_t_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), A_0);
				throw;
			}
		}
	}
}
