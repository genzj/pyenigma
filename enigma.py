class Tool:
    """
    Tool 

    An assistant class contains constants and static method.
    """
    alphabet=tuple([chr(i) for i in range(ord('a'),ord('z')+1)])
    ALPHABET=tuple([i.upper() for i in alphabet])
    
    @staticmethod
    def charat(i,tab=ALPHABET):
        """
        charat(int, iteratable) -> char

        Get the i-th char of tab, if i is larger than
        length of tab, i is set to i%len(tab).
        """
        return tab[i%len(tab)]

    @staticmethod
    def charoffset(c,offset,tab=ALPHABET):
        """
        charoffset(char, int, iteratable) -> char

        From the given char c, move forward for offset
        characters and return the target character.

        If c is None or "", calculation will be started
        from the beginning of tab, equivalent to method
        charat(...).
        
        If the sum of index of c and offset is larger
        than length of tab, only the reminder of 
        dividing sum to length will be kept.

        Raise IndexError if c is not in tab.
        """
        if not c: c=tab[0]
        return Tool.charat(tab.index(c)+offset)

class RotorFactory:
    """
    RotorFactory

    A factory composes rotors and reflectors with common
    key combinations.

    Currently 8 types of rotors and 5 types of reflectors
    are preloaded into factory class.

    To register custom key sets, simply add them to class
    __dict__ like following example:
        RotorFactory.KEYmy={'keytable':dict(zip(Tool.ALPHABET,
        'UVWXYZOPQRSTHIJKLMNABCDEFG')), 'notch':'G'}
    Thus you can get your customized rotor by NewRotor('my')

    With respect to reflectors, since they are not about
    to move during cipher process and thus no notch 
    required, only key dict required:
        RotorFactory.REFLECTORmy=dict(zip(Tool.ALPHABET,
        'ZYXWVUTSRQPONMLKJIHGFEDCBA'))
    And get this kind of reflector by NewReflector('my')
    """
    KEYI={'keytable':dict(zip(Tool.ALPHABET,'EKMFLGDQVZNTOWYHXUSPAIBRCJ')),
          'notch':'Q'}

    KEYII={'keytable':dict(zip(Tool.ALPHABET,'AJDKSIRUXBLHWTMCQGZNPYFVOE')),
           'notch':'E'}
    
    KEYIII={'keytable':dict(zip(Tool.ALPHABET,'BDFHJLCPRTXVZNYEIWGAKMUSQO')),
            'notch':'V'}
    
    KEYIV={'keytable':dict(zip(Tool.ALPHABET,'ESOVPZJAYQUIRHXLNFTGKDCMWB')),
            'notch':'J'}
    
    KEYV={'keytable':dict(zip(Tool.ALPHABET,'VZBRGITYUPSDNHLXAWMJQOFECK')),
            'notch':'Z'}
    
    KEYVI={'keytable':dict(zip(Tool.ALPHABET,'JPGVOUMFYQBENHZRDKASXLICTW')),
            'notch':'ZM'}

    KEYVII={'keytable':dict(zip(Tool.ALPHABET,'NZJHGRCXMYSWBOUFAIVLPEKQDT')),
            'notch':'ZM'}

    KEYVIII={'keytable':dict(zip(Tool.ALPHABET,'FKQHTLXOCBJSPDZRAMEWNIUYGV')),
            'notch':'ZM'}
    
    REFLECTORA=dict(zip(Tool.ALPHABET,'EJMZALYXVBWFCRQUONTSPIKHGD'))

    REFLECTORB=dict(zip(Tool.ALPHABET,'YRUHQSLDPXNGOKMIEBFZCWVJAT'))

    REFLECTORC=dict(zip(Tool.ALPHABET,'FVPJIAOYEDRZXWGCTKUQSBNMHL'))

    REFLECTORB_Thin=dict(zip(Tool.ALPHABET,'ENKQAUYWJICOPBLMDXZVFTHRGS'))

    REFLECTORC_Thin=dict(zip(Tool.ALPHABET,'RDOBJNTKVEHMLFCWZAXGYIPSUQ'))

    def NewReflector(name):
        """
        NewReflector(str) -> Rotor

        Get a new instance of registered reflector 
        instance by its name.

        A dict indicates key reflecting relationship 
        with name "REFLECTORname" must exist in namespace
        of this factory class.
        """
        return Rotor(getattr(RotorFactory,'REFLECTOR{}'.format(name)))

    def NewRotor(name):
        """
        NewRotor(str) -> Rotor

        Get a new instance of registered rotor instance 
        by its name.

        A with following structure
            {'keytable':dict, 'notch':str}
        with name "KEYname" must exist in namespace
        of this factory class.
        """
        return Rotor(**(getattr(RotorFactory,'KEY{}'.format(name))))

class Plugboard(dict):
    # TODO validate symmetry of each connection in __init__
    """
    Plugboard() -> new empty Plugboard
    Plugboard(mapping) -> new Plugboard initialized from a mapping object's
        (key, value) pairs
    Plugboard(iterable) -> new Plugboard initialized as if via:
        d = {}
        for k, v in iterable:
            d[k] = v
    Plugboard(**kwargs) -> new Plugboard initialized with the name=value pairs
        in the keyword argument list.  For example:  Plugboard('A'='Z', 'B'='Y')

    Changes to relationship of two keys are implemented 
    symmetrically by swapping involved keys. For example,
    `plugboard['A']='Z'` will connect 'A' to 'Z' as well as
    'Z' to 'A' if both 'A' and 'Z' haven't been connected
    to any other letters yet. Then going on executing 
    `plugboard['A']='B'` restores 'A'->'A' and 'Z'->'Z'
    prior to setting 'A'->'B' and 'B'->'A'.
    """
    def __setitem__(self,k,v):
        if self[k] == v: return
        self._reset(k)
        self._reset(v)
        self._swap(k,v)

    def _reset(self,k):
        """
        _reset(char) -> None

        Reset the given key back to itself.
        """
        v = self[k]
        if v != k: self._swap(k,v)

    def _swap(self,k1,k2):
        """
        _swap(char, char) -> None

        Swap connection of the two given keys.
        """
        if k1 == k2: return
        v1,v2 = self[k1],self[k2]
        super().__setitem__(k1,v2)
        super().__setitem__(k2,v1)

class Rotor:
    def __init__(self,keytable,notch='Z'):
        self.key=keytable
        self.notch=notch
        self.rev={v:k for k,v in self.key.items()}
        self.reset()
        self.chain(None,None)

    def chain(self,higher=None,lower=None):
        self.higher=higher
        self.lower=lower

    def reset(self):
        self.offset=0
        self.carry=False

    def move(self,offset='A',start='A'):
        self.reset()
        self.offset=(ord(offset)-ord(start))%len(self.key)

    def transitchar(self,c,forward=True):
        tab=self.key if forward else self.rev
        ret=tab[c[0]]
        return ret

    def incr(self,i=1):
        while i>0:
            self.offset+=1
            i-=1
            if Tool.charat(self.offset - 1) in self.notch:
                self.carry=True
                if self.higher: self.higher.incr()
            else:
                self.carry=False
            if self.offset >= len(self.key):
                self.offset -= len(self.key)


    def __len__(self):
        return len(self.key)

class Enigma:
    '''
    Enigma(Reflector, Rotor1, [Rotor2, ..., RotorN ] [, Plugboard])

    Create new Enigma object from given reflector, rotors
    and optional plugboard. If plugboard omitted, no swap
    of characters would happen.

    Rotor1 is the rotor directly connected to reflector,
    similarly RotorN is connected to plugboard.
    '''

    debug = 0 #Set debug to 1 to enable debugging outputs.
    
    def __init__(self,reflector,*rotors,plugboard=None):
        '''
        '''
        if not plugboard: plugboard = Plugboard(zip(Tool.ALPHABET,Tool.ALPHABET))
        self.reflector=reflector
        self.rotors=rotors
        self.plugboard=plugboard
        self._chain()

    def _applyplugboard(self,text):
        '''
        _applyplugboard(str) -> str

        Pass text to plugboard and return its transformed
        output.
    '''
        if not self.plugboard: return text
        return [self.plugboard[t] for t in text]
    
    def _chain(self):
        '''
        _chain() -> None

        Connect each rotor to its neighbours. Only
        called by __init__ of class.
    '''
        for i,r in enumerate(self.rotors):
            higher = self.rotors[i-1] if i > 0 else None
            lower = self.rotors[i+1] if i < len(self.rotors) - 1 else None
            r.chain(higher, lower)
            
    def setto(self,state):
        '''
        setto(str) -> None

        Move rotors to proper positions to reproduce a
        certain state.
        
        Length of state string is required to be identical
        to number of rotors. Otherwise an exception raised.

        See method state(...) for more.
        '''
        if len(state) != len(self.rotors):
            raise Exception()
        else:
            for r,s in zip(self.rotors,state):
                r.move(s)

    def _connect(self,c,ridx,direction):
        '''
        _connect(char, int, int) -> None

        Connect character c of the ridx-th rotor to its
        neighbour in the specified direction, return the
        corresponding character on next rotor.

        The sign of directions matters instead of
        its value. When direction < 0, move character from
        plugboard side to reflector side and vice versa.
        
    '''
        class DummyRotor:
            offset = 0

        c=c[0]
        if not direction:direction=1
        direction = direction//abs(direction)
        rs = ((DummyRotor,)  # Reflector\
            + self.rotors   # Rotors
            + (DummyRotor,)) # Plug board
        r1 = rs[ridx]
        r2 = rs[ridx+direction]
        L = len(self.reflector)
        offset = r1.offset - r2.offset
        s=Tool.charoffset(c,L-offset)
        self._debug('\tConnect R{}:{} to R{}:{}'.format(ridx,c,ridx+direction,s))
        return s
        
    def transitchar(self,c):
        """
        transitchar(str) -> char

        Lead the first character of cto go though current
        path of Enigma to decrypt/encrypt it.
    """
        c=c[0]
        self.rotors[-1].incr()
        rotor_idx=len(self.rotors)
        self._debug(self.__repr__())
        c=self._connect(c,len(self.rotors)+1,-1)
        for r in self.rotors[-1::-1]+(self.reflector,):
            s=r.transitchar(c,forward=True)
            self._debug('\tR{}: Change {} to {}'.format(rotor_idx,c,s))
            if rotor_idx > 0 : 
                c=self._connect(s,rotor_idx,-1)
                rotor_idx-=1

        for r in self.rotors:
            c=self._connect(s,rotor_idx,1)
            s=r.transitchar(c,forward=False)
            rotor_idx+=1
            self._debug('\tR{}: Change {} to {}'.format(rotor_idx,c,s))
            c=s
        c=self._connect(c,rotor_idx,1)
        return c

    def state(self):
        '''
        state() -> str

        Get a string indicates current position of each rotors
        in this machine. The left-most character of returned
        string denotes offset of the rotor directly connected
        to reflector.

        Pass state string to method 'setto(...)' to reproduce
        it.
        
        '''
        return "".join([chr(ord('A')+r.offset) for r in self.rotors])
        
    def __repr__(self):
        return "<Enigma '{}'>".format(self.state())

    def __call__(self,text):
        '''
        e(str) -> str

        Encrypt or decrypt the specified string.

        This method will increase state of current Enigma.
    '''
        return "".join(self._applyplugboard([self.transitchar(c) for c in self._applyplugboard(text)]))

    def _debug(self,*text):
        '''
    '''
        sys = __import__('sys')
        if getattr(self,'debug',None):print(file=sys.stderr,*text)

if __name__ == '__main__':
    ref=RotorFactory.NewReflector('B')
    r1=RotorFactory.NewRotor('I')
    r2=RotorFactory.NewRotor('II')
    r3=RotorFactory.NewRotor('III')
    e=Enigma(ref,r1,r2,r3)
    e.plugboard['A']='Z'
    e.plugboard['B']='Y'
    e.setto('ALI')
    encrypted='''NRFHFLOGTBIHURDAFCKTFONJTNGFMESQSLBQEQJILGJRNNBOUSDRGXJRIQQRJZQURVSYRLRDOFVBFKKKFFGXDNYXLWPNFPGDIDBOGXHDNBMDSQSAKPXJHSBWYXLWWCZHJBIEHKXXYZRTPITVDOGJILLRUMCVULWZMQDSRALFRPNIZIBMOUSCKPWBELJGZOLOOZXJMAANELTFYLOSZFGKYDLKJGRPDVNWULPEOKTKFDPGNYCJPENIPQBOFDZRBOHTSHZMOMYANWSAMKLRAGTROJEXNZTAIAJRDSDNHQVMMXDZMPTUTOMLOSNGSLOPGTYUJJNSEHQJGSODKYPAH'''
    print(e(encrypted))

